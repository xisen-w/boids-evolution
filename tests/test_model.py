"""OpenAICompatModel retry policy, with a fake client (no network, no key)."""
import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from boidsnet.runner import model as M

try:                                    # the SDK is only needed for paid runs (requirements.txt)
    import openai  # noqa: F401
    HAVE_OPENAI = True
except ImportError:
    HAVE_OPENAI = False


class FakeErr(Exception):
    def __init__(self, status):
        super().__init__(f"status {status}")
        self.status_code = status


def fake_client(errors):
    errs = list(errors)

    def create(**kw):
        if errs:
            raise errs.pop(0)
        msg = types.SimpleNamespace(content="ok")
        return types.SimpleNamespace(choices=[types.SimpleNamespace(message=msg)],
                                     usage=types.SimpleNamespace(prompt_tokens=3, completion_tokens=1))
    return types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=create)))


def make(errors, mode="strict"):
    m = M.OpenAICompatModel.__new__(M.OpenAICompatModel)
    m.client, m.name = fake_client(errors), "fake"
    m.send_temperature, m.token_param, m.param_mode, m.param_adaptations = True, "max_tokens", mode, []
    return m


class KeyGuardTests(unittest.TestCase):
    def test_no_key_load_without_os_isolation(self):
        """msg #105.4: model.py refuses on its own, independent of run.py."""
        from boidsnet.runner import sandbox
        old = (sandbox._LEVEL, os.environ.get("BOIDS_SANDBOX"))
        sandbox._LEVEL, os.environ["BOIDS_SANDBOX"] = None, "hook-only"
        os.environ["FAKE_KEY_FOR_GUARD"] = "k"
        try:
            with self.assertRaises(PermissionError) as cm:
                M.OpenAICompatModel("dep", "FAKE_KEY_FOR_GUARD", True)
            self.assertIn("isolation", str(cm.exception))
        finally:
            sandbox._LEVEL = old[0]
            os.environ.pop("FAKE_KEY_FOR_GUARD", None)
            if old[1] is None:
                os.environ.pop("BOIDS_SANDBOX", None)
            else:
                os.environ["BOIDS_SANDBOX"] = old[1]


class RetryTests(unittest.TestCase):
    def test_cached_tokens_recorded(self):
        m = make([])
        m.complete("s", "u", 0.7, 10)
        self.assertIsNone(m.last_cached_tokens)                         # API did not report it
        def create(**kw):
            return types.SimpleNamespace(
                choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="ok"))],
                usage=types.SimpleNamespace(prompt_tokens=9, completion_tokens=1,
                                            prompt_tokens_details=types.SimpleNamespace(cached_tokens=6)))
        m.client.chat.completions.create = create
        m.complete("s", "u", 0.7, 10)
        self.assertEqual(m.last_cached_tokens, 6)

    @mock.patch.object(M.time, "sleep", lambda s: None)
    def test_transient_errors_retried(self):
        m = make([FakeErr(429), FakeErr(503), ConnectionError("reset")])
        self.assertEqual(m.complete("s", "u", 0.7, 10), ("ok", 3, 1))
        self.assertEqual(m.last_retries, 3)

    @mock.patch.object(M.time, "sleep", lambda s: None)
    def test_auth_error_not_retried(self):
        m = make([FakeErr(401)])
        with self.assertRaises(FakeErr):
            m.complete("s", "u", 0.7, 10)
        self.assertEqual(m.last_retries, 0)

    @mock.patch.object(M.time, "sleep", lambda s: None)
    def test_gives_up_after_max_attempts(self):
        m = make([FakeErr(500)] * M.OpenAICompatModel.MAX_ATTEMPTS)
        with self.assertRaises(FakeErr):
            m.complete("s", "u", 0.7, 10)

    @unittest.skipUnless(HAVE_OPENAI, "openai SDK not installed (pip install -r requirements.txt)")
    def test_azure_client_constructed_without_network(self):
        os.environ["FAKE_AZ_KEY_X"] = "k"
        try:
            m = M.OpenAICompatModel("my-deployment", "FAKE_AZ_KEY_X", allow_spend=True,
                                    azure_endpoint="https://example.openai.azure.com",
                                    api_version="2024-06-01")
            self.assertEqual(type(m.client).__name__, "AzureOpenAI")
            self.assertEqual(m.name, "my-deployment")
        finally:
            del os.environ["FAKE_AZ_KEY_X"]

    @unittest.skipUnless(HAVE_OPENAI, "openai SDK not installed (pip install -r requirements.txt)")
    def test_transport_policy_and_required_api_version(self):
        """msg #134/#131: SDK retries off, explicit timeout; Azure api version never implicit."""
        os.environ["FAKE_AZ_KEY_Y"] = "k"
        try:
            with self.assertRaises(ValueError):
                M.OpenAICompatModel("dep", "FAKE_AZ_KEY_Y", True, azure_endpoint="https://example.openai.azure.com")
            m = M.OpenAICompatModel("dep", "FAKE_AZ_KEY_Y", True, azure_endpoint="https://example.openai.azure.com",
                                    api_version="2025-01-01-preview")
            self.assertEqual(m.client.max_retries, 0)
            self.assertEqual(float(m.client.timeout), M.OpenAICompatModel.REQUEST_TIMEOUT_S)
            tp = m.transport_policy()
            self.assertEqual((tp["sdk_max_retries"], tp["runner_max_attempts"], tp["api_version"]),
                             (0, 6, "2025-01-01-preview"))
        finally:
            del os.environ["FAKE_AZ_KEY_Y"]

    def test_param_rejection_strict_refuses(self):
        m = make([FakeErr(400)])
        m.client.chat.completions.create  # noqa
        with self.assertRaises(FakeErr):
            m.complete("s", "u", 0.7, 10)

    def test_param_rejection_auto_adapts_and_records(self):
        class P(FakeErr):
            def __str__(self):
                return "Unsupported value: 'temperature' does not support 0.7"
        class Q(FakeErr):
            def __str__(self):
                return "Unsupported parameter: 'max_tokens' is not supported; use 'max_completion_tokens'"
        m = make([P(400), Q(400)], mode="auto")
        self.assertEqual(m.complete("s", "u", 0.7, 10)[0], "ok")
        self.assertFalse(m.send_temperature)
        self.assertEqual(m.token_param, "max_completion_tokens")
        self.assertEqual(len(m.param_adaptations), 2)

    def test_refuses_without_spend_or_key(self):
        with self.assertRaises(PermissionError):
            M.OpenAICompatModel("x", "NO_SUCH_KEY_VAR", allow_spend=False)
        with self.assertRaises(PermissionError):
            M.OpenAICompatModel("x", "NO_SUCH_KEY_VAR_123", allow_spend=True)


if __name__ == "__main__":
    unittest.main()
