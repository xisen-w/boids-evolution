"""Strict re-audit counterexamples. Artificial fixtures and loopback HTTP only."""
import json
import os
from pathlib import Path
import signal
import tempfile
import threading
import time
import types
import unittest
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest import mock

from boidsnet.runner import sandbox
from boidsnet.runner.library import Library
from boidsnet.runner.mechanisms import tci_score
from boidsnet.runner.model import RequestDeadlineExceeded
from boidsnet.runner.sac_pilot import Budget, read_json, DEFAULT_CONFIG
from tests.test_model import make

IDENT = "def execute(table, lookup):\n    return table\n"
CALL = {"args": [[{"units": 1.0}], []], "kwargs": {}}


class SandboxReauditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.lib = Library(self.tmp.name)

    def add(self, tid, code, acl=()):
        return self.lib.add(tid, int(tid[1:3]), int(tid[-2:]), "fixture", "fixture", None, code, acl=acl)

    def test_caught_permission_error_cannot_disable_acl(self):
        self.add("a00_r01", "import sys\ndef execute(table, lookup):\n"
                 "    fn = sys.modules['tools.a01_r02'].execute\n"
                 "    try:\n        return fn(table, lookup)\n"
                 "    except BaseException:\n        return fn(table, lookup)\n")
        self.add("a01_r02", "def execute(table, lookup):\n    return [{'future': 1}]\n", ["a00_r01"])
        Path(self.lib.pkg, "solver_t000_k0.py").write_text(
            "from tools import a01_r02, a00_r01\ndef execute(table, lookup):\n"
            "    return a00_r01.execute(table, lookup)\n")
        acl = dict(self.lib.acl, solver_t000_k0=["a00_r01", "a01_r02"])
        rows = sandbox.run_tool(self.lib.root, "solver_t000_k0", [CALL, CALL], acl=acl)
        self.assertTrue(all("PermissionError" in row.get("__error__", "") for row in rows), rows)

    def test_policy_hook_cannot_be_switched_off(self):
        self.add("a00_r01", "import sys\ndef execute(table, lookup):\n    sys.setprofile(None)\n    return table\n")
        self.assertIn("PermissionError", sandbox.run_tool(self.lib.root, "a00_r01", [CALL])[0]["__error__"])

    def test_writable_module_name_cannot_change_tool_identity(self):
        self.add("a00_r01", "import sys\ndef execute(table, lookup):\n"
                 "    global __name__\n    __name__ = 'not_a_tool'\n"
                 "    return sys.modules['tools.a01_r02'].execute(table, lookup)\n")
        self.add("a01_r02", "def execute(table, lookup):\n    return [{'future': 1}]\n", ["a00_r01"])
        Path(self.lib.pkg, "solver_t000_k0.py").write_text(
            "from tools import a01_r02, a00_r01\ndef execute(table, lookup):\n"
            "    return a00_r01.execute(table, lookup)\n")
        acl = dict(self.lib.acl, solver_t000_k0=["a00_r01", "a01_r02"])
        row = sandbox.run_tool(self.lib.root, "solver_t000_k0", [CALL], acl=acl)[0]
        self.assertIn("PermissionError", row.get("__error__", ""), row)

    def test_future_source_is_not_readable_from_an_old_tool(self):
        self.add("a00_r01", "import os\ndef execute(table, lookup):\n"
                 "    p = os.path.join(os.path.dirname(__file__), 'a01_r02.py')\n"
                 "    return open(p).read()\n")
        self.add("a01_r02", IDENT, ["a00_r01"])
        Path(self.lib.pkg, "solver_t000_k0.py").write_text(
            "from tools import a01_r02, a00_r01\ndef execute(table, lookup):\n"
            "    return a00_r01.execute(table, lookup)\n")
        acl = dict(self.lib.acl, solver_t000_k0=["a00_r01", "a01_r02"])
        row = sandbox.run_tool(self.lib.root, "solver_t000_k0", [CALL], acl=acl)[0]
        self.assertIn("PermissionError", row.get("__error__", ""), row)

    def test_nonstring_module_name_does_not_break_policy(self):
        self.add("a00_r01", "__name__ = 17\n" + IDENT)
        self.assertEqual(sandbox.run_tool(self.lib.root, "a00_r01", [CALL]), [CALL["args"][0]])

    def test_os_open_write_flags_blocked_and_probes_do_not_change_source(self):
        for flag in ("os.O_WRONLY", "os.O_RDWR", "os.O_WRONLY | os.O_TRUNC",
                     "os.O_WRONLY | os.O_APPEND", "os.O_RDONLY | os.O_CREAT"):
            with self.subTest(flag=flag), tempfile.TemporaryDirectory() as tmp:
                lib = Library(tmp)
                code = ("import os\ndef execute(table, lookup):\n"
                        f"    fd = os.open(__file__, {flag})\n"
                        "    os.write(fd, b'corrupted')\n    os.close(fd)\n    return table\n")
                lib.add("a00_r01", 0, 1, "fixture", "fixture", None, code)
                rows = sandbox.run_tool(tmp, "a00_r01", [CALL, CALL])
                self.assertTrue(all("PermissionError" in row.get("__error__", "") for row in rows), rows)
                self.assertEqual(Path(lib.pkg, "a00_r01.py").read_text(), code)

    def test_os_open_read_still_allowed(self):
        self.add("a00_r01", "import os\ndef execute(table, lookup):\n"
                 "    fd = os.open(__file__, os.O_RDONLY)\n    os.close(fd)\n    return table\n")
        self.assertEqual(sandbox.run_tool(self.lib.root, "a00_r01", [CALL]), [CALL["args"][0]])

    def test_tool_exits_are_failures_after_readiness(self):
        for body in ("import os\nos._exit(7)\n", "import os\ndef execute(table, lookup):\n    os._exit(7)\n",
                     "import os\ndef execute(table, lookup):\n    os._exit(0)\n"):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as tmp:
                lib = Library(tmp)
                lib.add("a00_r01", 0, 1, "fixture", "fixture", None, body)
                rows = sandbox.run_tool(tmp, "a00_r01", [CALL, CALL])
                self.assertTrue(all("terminated without a result" in r.get("__error__", "") for r in rows), rows)

    def test_worker_initialization_failure_is_not_a_tool_zero(self):
        self.add("a00_r01", IDENT)
        with mock.patch.object(sandbox, "_WORKER", "raise RuntimeError('fixture startup')"):
            with self.assertRaises(sandbox.SandboxInfrastructureError):
                sandbox.run_tool(self.lib.root, "a00_r01", [CALL])

    def test_worker_initialization_timeout_is_infrastructure(self):
        self.add("a00_r01", IDENT)
        with mock.patch.object(sandbox, "_WORKER", "while True: pass"):
            with self.assertRaises(sandbox.SandboxInfrastructureError):
                sandbox.run_tool(self.lib.root, "a00_r01", [CALL], timeout_s=0.1)

    def test_tool_corrupting_result_pipe_is_not_infrastructure(self):
        self.add("a00_r01", "import os, __main__\ndef execute(table, lookup):\n"
                 "    os.write(__main__.RESULT_FD, b'not-json')\n    return table\n")
        row = sandbox.run_tool(self.lib.root, "a00_r01", [CALL])[0]
        self.assertEqual(row, {"__error__": "tool corrupted its result channel"})

    def test_namespace_tool_mount_read_only_before_pivot(self):
        # This checks construction only. The separate OS test is authoritative
        # for runtime mounting and is explicitly skipped on macOS.
        code = sandbox._NS_SCRIPT
        self.assertIn('mount -o remount,ro "$R/sandbox"', code)
        self.assertLess(code.index('mount -o remount,ro "$R/sandbox"'), code.index("pivot_root"))

    def test_os_mount_read_only_even_if_hook_policy_is_tampered(self):
        if not sandbox.isolation_level().startswith("os-"):
            self.skipTest("Linux OS namespace validation unavailable on this host")
        self.add("a00_r01", "import os, __main__\ndef execute(table, lookup):\n"
                 "    __main__._hook.__code__ = (lambda *args: None).__code__\n"
                 "    fd = os.open(__file__, os.O_WRONLY | os.O_TRUNC)\n"
                 "    os.write(fd, b'corrupted')\n    os.close(fd)\n    return table\n")
        row = sandbox.run_tool(self.lib.root, "a00_r01", [CALL])[0]
        self.assertIn("Read-only file system", row.get("__error__", ""), row)


class StaticImportReauditTests(unittest.TestCase):
    def test_all_supported_absolute_relative_forms_have_same_dependency_and_tci(self):
        prefixes = ("from tools import a00_r01", "import tools.a00_r01",
                    "from tools.a00_r01 import execute", "from . import a00_r01",
                    "from .a00_r01 import execute")
        with tempfile.TemporaryDirectory() as tmp:
            lib = Library(tmp)
            scores = []
            for prefix in prefixes:
                source = prefix + "\n" + IDENT
                self.assertEqual(lib.static_imports(source), ["a00_r01"], prefix)
                scores.append(tci_score(source, lib.static_imports(source), ["a00_r01"]))
            self.assertEqual(len(set(scores)), 1)

    def test_relative_dependency_executes_and_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = Library(tmp)
            lib.add("a00_r01", 0, 1, "fixture", "fixture", None, IDENT)
            e = lib.add("a01_r02", 1, 2, "fixture", "fixture", None,
                        "from . import a00_r01\ndef execute(table, lookup):\n"
                        "    return a00_r01.execute(table, lookup)\n", acl=["a00_r01"])
            self.assertEqual(e["static_imports"], ["a00_r01"])
            self.assertEqual(sandbox.run_tool(tmp, "a01_r02", [CALL]), [CALL["args"][0]])


class DeadlineReauditTests(unittest.TestCase):
    def test_total_deadline_closes_client_without_retry_and_restores_alarm(self):
        m = make([])
        m.REQUEST_TIMEOUT_S = 0.03
        m.before_request = mock.Mock()
        m.client.close = mock.Mock()
        m.client.chat.completions.create = mock.Mock(side_effect=lambda **kw: time.sleep(5))
        previous = signal.getsignal(signal.SIGALRM)
        start = time.monotonic()
        with self.assertRaises(RequestDeadlineExceeded):
            m.complete("s", "u", 0.7, 10)
        self.assertLess(time.monotonic() - start, 1)
        self.assertEqual(m.before_request.call_count, 1)
        self.assertEqual(m.client.chat.completions.create.call_count, 1)
        m.client.close.assert_called_once()
        self.assertEqual(signal.getsignal(signal.SIGALRM), previous)
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL), (0, 0))
        with self.assertRaises(RequestDeadlineExceeded):
            m.complete("s", "u", 0.7, 10)
        self.assertEqual(m.before_request.call_count, 1)

    def test_deadline_setup_failure_makes_no_request_or_reservation(self):
        m = make([])
        m.before_request = mock.Mock()
        m.client.chat.completions.create = mock.Mock()
        with mock.patch("boidsnet.runner.model.signal.getitimer", return_value=(10, 0)):
            with self.assertRaisesRegex(RuntimeError, "alarm is active"):
                m.complete("s", "u", 0.7, 10)
        with ThreadPoolExecutor(max_workers=1) as pool:
            with self.assertRaisesRegex(RuntimeError, "main thread"):
                pool.submit(m.complete, "s", "u", 0.7, 10).result()
        m.client.chat.completions.create.assert_not_called()
        m.before_request.assert_not_called()

    def test_trickling_loopback_response_cannot_extend_deadline(self):
        import httpx
        from openai import OpenAI
        stop = threading.Event()
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_POST(self):
                requests.append(self.path)
                self.rfile.read(int(self.headers["Content-Length"]))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", "100000")
                self.end_headers()
                try:
                    for _ in range(100):
                        if stop.is_set():
                            break
                        self.wfile.write(b" ")
                        self.wfile.flush()
                        stop.wait(0.01)
                except (BrokenPipeError, ConnectionResetError):
                    pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        server.timeout = 1
        worker = threading.Thread(target=server.handle_request, daemon=True)
        worker.start()
        m = make([])
        m.REQUEST_TIMEOUT_S = 0.15
        m.client = OpenAI(api_key="FAKE_LOCAL_FIXTURE", base_url=f"http://127.0.0.1:{server.server_port}/v1",
                          timeout=1, max_retries=0,
                          http_client=httpx.Client(trust_env=False, follow_redirects=False))
        try:
            start = time.monotonic()
            with self.assertRaises(RequestDeadlineExceeded):
                m.complete("s", "u", 0.7, 10)
            self.assertLess(time.monotonic() - start, 1)
            self.assertEqual(len(requests), 1)
            self.assertTrue(m.client.is_closed())
        finally:
            stop.set()
            m.client.close()
            worker.join(timeout=2)
            server.server_close()


class AccountingReauditTests(unittest.TestCase):
    def test_malformed_provider_usage_is_terminal_not_negative_cost(self):
        for tin, tout, cache in ((-100, 1, None), (1, -1, None), (True, 1, None),
                                (1.5, 1, None), (float("nan"), 1, None), (2, 1, 3), (2, 1, -1)):
            with self.subTest(usage=(tin, tout, cache)):
                m = make([])
                m.after_response = mock.Mock()
                m.client.chat.completions.create = mock.Mock(return_value=types.SimpleNamespace(
                    choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="ok"))],
                    usage=types.SimpleNamespace(prompt_tokens=tin, completion_tokens=tout,
                                                prompt_cache_hit_tokens=cache)))
                with self.assertRaises(RuntimeError):
                    m.complete("s", "u", 0.7, 10)
                self.assertEqual(m.client.chat.completions.create.call_count, 1)
                m.after_response.assert_not_called()

    def test_billed_usage_retained_when_choice_missing(self):
        m = make([])
        m.after_response = mock.Mock()
        m.client.chat.completions.create = mock.Mock(return_value=types.SimpleNamespace(
            choices=[], usage=types.SimpleNamespace(prompt_tokens=3, completion_tokens=1)))
        with self.assertRaisesRegex(RuntimeError, "assistant choice"):
            m.complete("s", "u", 0.7, 10)
        m.after_response.assert_called_once()
        self.assertEqual(m.after_response.call_args.args[:3], (3, 1, None))
        self.assertEqual(m.client.chat.completions.create.call_count, 1)

    def test_budget_refuses_invalid_or_duplicate_usage_and_stays_closed(self):
        for tin, tout, cache in ((-1, 1, None), (1, 1, 2), (1000, 1, None), (1, 11, None)):
            with self.subTest(usage=(tin, tout, cache)), tempfile.TemporaryDirectory() as tmp:
                b = Budget(read_json(DEFAULT_CONFIG), Path(tmp) / "ledger.jsonl")
                b.before("s", "u", 10, 0)
                with self.assertRaises((RuntimeError, PermissionError)):
                    b.after(tin, tout, cache, {})
                self.assertGreaterEqual(b.reported_usd, 0)
                with self.assertRaises(PermissionError):
                    b.before("s", "u", 10, 1)
        with tempfile.TemporaryDirectory() as tmp:
            b = Budget(read_json(DEFAULT_CONFIG), Path(tmp) / "ledger.jsonl")
            b.before("s", "u", 10, 0)
            b.after(3, 1, 1, {})
            amount = b.reported_usd
            with self.assertRaises(RuntimeError):
                b.after(3, 1, 1, {})
            self.assertEqual(b.reported_usd, amount)

    def test_budget_retains_unanswered_retry_reservations(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Budget(read_json(DEFAULT_CONFIG), Path(tmp) / "ledger.jsonl")
            b.before("s", "u", 10, 0)
            first = b.reserved
            b.before("s", "u", 10, 1)
            b.after(3, 1, 1, {})
            self.assertEqual(b.requests, 2)
            self.assertEqual(b.reported_responses, 1)
            self.assertAlmostEqual(b.reserved, first * 2)


if __name__ == "__main__":
    unittest.main()
