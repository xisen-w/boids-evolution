"""Adversarial offline regressions for the October strict audit (no API calls)."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest import mock

from boidsnet.runner.env_adapter import MechEnv
from boidsnet.runner.exposure import summarise
from boidsnet.runner.library import Library
from boidsnet.runner.run import DEFAULT_ENV
from boidsnet.runner.sandbox import run_tool, SandboxInfrastructureError
from boidsnet.runner.sac_pilot import resolve, read_json, DEFAULT_CONFIG, approval_template, execute, verify_approval
from boidsnet.runner.utility import glue_gate, score_society, freeze_library, StubSolver
from tests.test_model import make, FakeErr

IDENT = "def execute(table, lookup, **params):\n    return table\n"
CALL = {"args": [[{"units": 1.0}], []], "kwargs": {}}


class SandboxRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.lib = Library(self.tmp.name)

    def add(self, tid, code, acl=()):
        self.lib.add(tid, 0, 1, "fixture", "fixture", None, code, acl=acl)

    def test_cached_imports_cannot_expand_historical_acl(self):
        self.add("a01_r02", "def execute(table, lookup):\n    return [{'future': 1}]\n", ["a00_r01"])
        for form in ("from tools import a01_r02\n    return a01_r02.execute(table, lookup)",
                     "import importlib\n    m = importlib.import_module('tools.a01_r02')\n    return m.execute(table, lookup)",
                     "import sys\n    return sys.modules['tools.a01_r02'].execute(table, lookup)",
                     "from . import a01_r02\n    return a01_r02.execute(table, lookup)"):
            # Only our fixture changes between subcases, never an experiment output.
            Path(self.lib.pkg, "a00_r01.py").write_text("def execute(table, lookup):\n    " + form + "\n")
            solver = "from tools import a01_r02, a00_r01\ndef execute(table, lookup):\n    return a00_r01.execute(table, lookup)\n"
            Path(self.lib.pkg, "solver_t000_k0.py").write_text(solver)
            acl = {"a00_r01": [], "a01_r02": ["a00_r01"], "solver_t000_k0": ["a00_r01", "a01_r02"]}
            with self.subTest(form=form):
                self.assertIn("PermissionError", run_tool(self.lib.root, "solver_t000_k0", [CALL], acl=acl)[0]["__error__"])

    def test_stdout_stderr_and_import_prints_do_not_corrupt_result(self):
        self.add("a00_r01", "import os, sys\nprint('import debug')\ndef execute(table, lookup):\n"
                 "    print('debug')\n    print('stderr', file=sys.stderr)\n    os.write(1, b'raw')\n    return table\n")
        self.assertEqual(run_tool(self.lib.root, "a00_r01", [CALL]), [CALL["args"][0]])

    def test_each_probe_has_clean_builtins_and_stdlib_state(self):
        self.add("a00_r01", "import builtins, json\ndef execute(table, lookup):\n"
                 "    builtins.fixture_count = getattr(builtins, 'fixture_count', 0) + 1\n"
                 "    json.fixture_count = getattr(json, 'fixture_count', 0) + 1\n"
                 "    return [builtins.fixture_count, json.fixture_count]\n")
        self.assertEqual(run_tool(self.lib.root, "a00_r01", [CALL] * 3), [[1, 1]] * 3)

    def test_hash_seed_fixed_across_processes_and_parent_settings(self):
        self.add("a00_r01", "def execute(table, lookup):\n    return [hash('boids'), list(set(['a', 'b', 'c', 'd']))]\n")
        rows = []
        for parent in ("random", "1", "42", ""):
            with mock.patch.dict(os.environ, {"PYTHONHASHSEED": parent}):
                rows.append(run_tool(self.lib.root, "a00_r01", [CALL])[0])
        self.assertTrue(all(row == rows[0] for row in rows))

    def test_timeout_is_tool_failure_not_infrastructure(self):
        self.add("a00_r01", "def execute(table, lookup):\n    while True: pass\n")
        rows = run_tool(self.lib.root, "a00_r01", [CALL] * 2, timeout_s=0.1)
        self.assertEqual(rows, [{"__error__": "timeout"}] * 2)

    def test_launch_nonzero_and_invalid_transport_abort(self):
        self.add("a00_r01", IDENT)
        cases = [subprocess.CompletedProcess([], 1, "", "mount failed"),
                 subprocess.CompletedProcess([], 0, "debug []", ""),
                 subprocess.CompletedProcess([], 0, '{"protocol":1,"outputs":{}}', "")]
        for result in cases:
            with mock.patch("boidsnet.runner.sandbox.isolation_level", return_value="hook-only"), \
                    mock.patch("boidsnet.runner.sandbox.subprocess.run", return_value=result):
                with self.assertRaises(SandboxInfrastructureError):
                    run_tool(self.lib.root, "a00_r01", [CALL])
        with mock.patch("boidsnet.runner.sandbox.isolation_level", return_value="hook-only"), \
                mock.patch("boidsnet.runner.sandbox.subprocess.run", side_effect=FileNotFoundError):
            with self.assertRaises(SandboxInfrastructureError):
                run_tool(self.lib.root, "a00_r01", [CALL])

    def test_namespace_preparation_failure_is_also_infrastructure(self):
        self.add("a00_r01", IDENT)
        with mock.patch("boidsnet.runner.sandbox.isolation_level", return_value="os-fixture"), \
                mock.patch("boidsnet.runner.sandbox._ns_cmd", side_effect=RuntimeError("missing root")):
            with self.assertRaises(SandboxInfrastructureError):
                run_tool(self.lib.root, "a00_r01", [CALL])

    def test_harness_does_not_swallow_infrastructure_errors(self):
        env = MechEnv(DEFAULT_ENV)
        bad = mock.Mock(side_effect=SandboxInfrastructureError("fixture"))
        with self.assertRaises(SandboxInfrastructureError):
            env.m.harness(bad, env.m.tasks(0, "dev")[0])
        with self.assertRaises(SandboxInfrastructureError):
            env.m.behaviour_vector(bad, "signal")
        with self.assertRaises(SandboxInfrastructureError):
            env.m.behaviour_signature(bad, "signal")


class ApprovalRegressions(unittest.TestCase):
    def test_concurrent_launches_can_claim_approval_only_once(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch("boidsnet.runner.sandbox.isolation_level", return_value="os-fixture"), \
                mock.patch("boidsnet.runner.model.OpenAICompatModel", side_effect=RuntimeError("fixture")) as model:
            out = Path(tmp) / "one"
            r = resolve(read_json(DEFAULT_CONFIG), out)
            a = approval_template(r) | {"approved": True, "status": "APPROVED", "reviewed_by": "fixture"}
            def launch(_):
                try:
                    execute(r, a, out, True)
                except Exception as exc:
                    return type(exc)
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(launch, range(2)))
            self.assertCountEqual(results, [RuntimeError, FileExistsError])
            self.assertEqual(model.call_count, 1)

    def test_solver_infrastructure_failure_marks_pilot_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch("boidsnet.runner.sandbox.isolation_level", return_value="os-fixture"), \
                mock.patch("boidsnet.runner.model.OpenAICompatModel") as model, \
                mock.patch("boidsnet.runner.society.Society") as society, \
                mock.patch("boidsnet.runner.utility.score_society", side_effect=SandboxInfrastructureError("fixture")):
            model.return_value.sampling.return_value = {}
            model.return_value.transport_policy.return_value = {}
            society.return_value.run.return_value = {"records": 12, "truncated": False}
            out = Path(tmp) / "one"
            r = resolve(read_json(DEFAULT_CONFIG), out)
            a = approval_template(r) | {"approved": True, "status": "APPROVED", "reviewed_by": "fixture"}
            with self.assertRaises(RuntimeError):
                execute(r, a, out, True)
            failed = json.loads((out / "FAILED.json").read_text())
            self.assertEqual(failed["error_type"], "SandboxInfrastructureError")
            self.assertEqual(failed["completed_arms"], [])
            self.assertFalse((out / "pilot_summary.json").exists())

    def test_approval_rejects_another_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = resolve(read_json(DEFAULT_CONFIG), Path(tmp) / "one")
            a = approval_template(r) | {"approved": True, "status": "APPROVED", "reviewed_by": "fixture"}
            with mock.patch("boidsnet.runner.model.OpenAICompatModel") as model:
                with self.assertRaises(PermissionError):
                    execute(r, a, Path(tmp) / "two", True)
                model.assert_not_called()

    def test_live_source_revalidated_even_for_programmatic_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = resolve(read_json(DEFAULT_CONFIG), Path(tmp) / "one")
            a = approval_template(r) | {"approved": True, "status": "APPROVED", "reviewed_by": "fixture"}
            with mock.patch("boidsnet.runner.sac_pilot.code_hash", return_value="changed"):
                with self.assertRaises(PermissionError):
                    verify_approval(r, a, True, Path(tmp) / "one")

    def test_failed_run_consumes_approval_even_after_output_removed(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch("boidsnet.runner.sandbox.isolation_level", return_value="os-fixture"), \
                mock.patch("boidsnet.runner.model.OpenAICompatModel", side_effect=SandboxInfrastructureError("fixture")) as model:
            out = Path(tmp) / "one"
            r = resolve(read_json(DEFAULT_CONFIG), out)
            a = approval_template(r) | {"approved": True, "status": "APPROVED", "reviewed_by": "fixture"}
            with self.assertRaises(RuntimeError):
                execute(r, a, out, True)
            self.assertEqual(json.loads((out / "FAILED.json").read_text())["status"], "INCOMPLETE_NOT_SCORED_AS_ZERO")
            shutil.rmtree(out)  # disposable fixture only
            with self.assertRaises(FileExistsError):
                execute(r, a, out, True)
            self.assertEqual(model.call_count, 1)


class LibraryAndGlueRegressions(unittest.TestCase):
    def test_deepseek_redirect_does_not_make_an_unbudgeted_second_request(self):
        import httpx
        from openai import APIStatusError
        from boidsnet.runner.model import OpenAICompatModel
        requests, reservations = [], mock.Mock()
        def handler(request):
            requests.append(request)
            return httpx.Response(302, headers={"location": "https://redirect.invalid/chat/completions"},
                                  json={"error": "fixture redirect"})
        with httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False, trust_env=False) as http, \
                mock.patch("openai.DefaultHttpxClient", return_value=http) as factory, \
                mock.patch("boidsnet.runner.sandbox.isolation_level", return_value="os-fixture"), \
                mock.patch.dict(os.environ, {"BOIDS_PARTNER_API_KEY": "FAKE_NOT_A_KEY", "BOIDS_SANDBOX": "auto"}):
            m = OpenAICompatModel("deepseek-flash", "BOIDS_PARTNER_API_KEY", True,
                                   base_url="https://api.deepseek.com", thinking="disabled", before_request=reservations)
            with self.assertRaises(APIStatusError):
                m.complete("s", "u", 0.7, 10)
            factory.assert_called_once_with(follow_redirects=False)
            self.assertFalse(m.transport_policy()["follow_redirects"])
            self.assertEqual(len(requests), 1)
            self.assertEqual(reservations.call_count, 1)

    def test_freeze_preserves_lazy_acl_dependencies_but_hides_them_from_solver(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = Library(str(Path(tmp) / "library"))
            e = lib.add("a00_r01", 0, 1, "old", "old", None, IDENT)
            e["signature_signal"] = ["ERR:RuntimeError"] * 8
            src = ("import importlib\ndef execute(table, lookup):\n"
                   "    return importlib.import_module('tools.a00_r01').execute(table, lookup)\n")
            e = lib.add("a01_r02", 1, 2, "new", "new", None, src, acl=["a00_r01"])
            e["signature_signal"] = ["fixture"] * 8
            lib.save()
            frozen = str(Path(tmp) / "frozen")
            kept, _, meta = freeze_library(tmp, frozen)
            self.assertEqual([e["id"] for e in kept], ["a01_r02"])
            self.assertEqual(meta["dependency_only"], ["a00_r01"])
            self.assertEqual(run_tool(frozen, "a01_r02", [CALL]), [CALL["args"][0]])

    def test_library_rejects_path_traversal_and_existing_unindexed_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = Library(tmp)
            with self.assertRaises(ValueError):
                lib.add("../escape", 0, 1, "x", "x", None, IDENT)
            planted = Path(lib.pkg) / "a00_r01.py"
            planted.write_text("fixture")
            with self.assertRaises(FileExistsError):
                lib.add("a00_r01", 0, 1, "x", "x", None, IDENT)
            self.assertEqual(planted.read_text(), "fixture")

    def test_last_attempt_parameter_adaptation_does_not_return_none(self):
        class Unsupported(FakeErr):
            def __str__(self):
                return "Unsupported temperature"
        m = make([Unsupported(400)], mode="auto")
        m.MAX_ATTEMPTS = 1
        with self.assertRaises(Unsupported):
            m.complete("s", "u", 0.7, 10)

    def test_existing_library_metadata_and_source_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = Library(tmp)
            lib.add("a00_r01", 0, 1, "fixture", "fixture", None, IDENT)
            before = {str(p.relative_to(tmp)): p.read_bytes() for p in Path(tmp).rglob("*") if p.is_file()}
            with self.assertRaises(FileExistsError):
                Library(tmp)
            after = {str(p.relative_to(tmp)): p.read_bytes() for p in Path(tmp).rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_catalogue_retains_signature_and_implements_after_long_description(self):
        e = {"id": "a00_r01", "author": 0, "description": "x" * 1000, "implements": ["filter", "sort"]}
        s = summarise(e, "def execute(table, lookup, col, op, value):\n    return table\n")
        self.assertIn("execute(table, lookup, col, op, value)", s)
        self.assertIn("implements: filter, sort", s)
        self.assertLessEqual(len(s), 400)

    def test_glue_must_return_library_derived_value_not_dead_call(self):
        prefix = "from tools import a00_r01\ndef execute(table, lookup):\n"
        for tail in ("return []", "return table", "x = table\n    return x", "x = []\n    return x"):
            source = prefix + "    x = a00_r01.execute(table, lookup)\n    " + tail + "\n"
            self.assertFalse(glue_gate(source, {"a00_r01"})[0], source)
        source = prefix + "    x = a00_r01.execute(table, lookup)\n    y = x\n    return y\n"
        self.assertTrue(glue_gate(source, {"a00_r01"})[0])

    def test_dev_private_audit_keeps_replay_evidence_without_public_outcomes(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = Library(str(Path(tmp) / "library"))
            e = lib.add("a00_r01", 0, 1, "fixture", "identity", None, IDENT)
            e["signature_signal"] = ["fixture"] * 8
            lib.save()
            env = MechEnv(DEFAULT_ENV)
            tid = env.dev_tasks()[0]["id"]
            score_society(tmp, env, StubSolver(), attempts=1, split="dev", task_ids=[tid])
            public = json.loads(Path(tmp, "utility_dev/solver_log.jsonl").read_text())
            self.assertFalse({"passed", "verdict", "imported", "response"} & public.keys())
            audit = Path(tmp, "utility_dev/private_audit/task_000_attempt_0.json")
            record = json.loads(audit.read_text())
            self.assertEqual(record["status"], "SCORED")
            self.assertTrue({"system", "prompt", "response", "code", "verdict", "passed", "imported", "coverage_probe_seeds"} <= record.keys())
            self.assertEqual(audit.stat().st_mode & 0o777, 0o600)
            self.assertEqual(audit.parent.stat().st_mode & 0o777, 0o700)

    def test_local_client_errors_and_redirects_not_retried(self):
        for error in (TypeError("fixture"), ValueError("fixture"), FakeErr(302)):
            m = make([])
            m.client.chat.completions.create = mock.Mock(side_effect=error)
            with self.assertRaises(type(error)):
                m.complete("s", "u", 0.7, 10)
            self.assertEqual(m.client.chat.completions.create.call_count, 1)
            self.assertEqual(m.last_retries, 0)


if __name__ == "__main__":
    unittest.main()
