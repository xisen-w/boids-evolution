"""U harness: glue gate, library freeze, sealed scoring (stub solver)."""
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from boidsnet.runner.config import RunConfig
from boidsnet.runner.env_adapter import MechEnv
from boidsnet.runner.model import StubModel
from boidsnet.runner.society import Society
from boidsnet.runner.utility import (glue_gate, freeze_library, score_society, StubSolver, check_sampling,
                            solver_prompt, PUBLISHED_TEST_SEAL, main as umain)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.path.join(ROOT, "boidsnet", "env", "mechenv.py")
CAT = {"a00_r01", "a01_r02"}
OKG = ("from tools import a00_r01, a01_r02\n"
       "def execute(table, lookup, **params):\n"
       "    x = a00_r01.execute(table, lookup)\n"
       "    y = a01_r02.execute(x, lookup, col='units', k=3)\n"
       "    return y\n")


def body(lines):
    return "from tools import a00_r01\ndef execute(table, lookup, **params):\n" + \
        "".join("    " + l + "\n" for l in lines)


class GateTests(unittest.TestCase):
    def test_accepts_tool_chain(self):
        ok, reason, imp = glue_gate(OKG, CAT)
        self.assertTrue(ok, reason)
        self.assertEqual(imp, ["a00_r01", "a01_r02"])

    def test_rejects_logic(self):
        bad = {
            "loop": ["for r in table:", "    pass", "return table"],
            "comprehension": ["x = [r for r in table]", "return x"],
            "subscript": ["return a00_r01.execute(table[:3], lookup)"],
            "arithmetic": ["x = a00_r01.execute(table, lookup)", "return x + x"],
            "builtin": ["x = a00_r01.execute(sorted(table), lookup)", "return x"],
            "getattr": ["f = getattr(a00_r01, 'execute')", "return f(table, lookup)"],
            "conditional": ["if table:", "    return a00_r01.execute(table, lookup)", "return table"],
            "no_call": ["return table"],
            "lambda": ["f = lambda t: t", "return a00_r01.execute(table, lookup)"],
            "unbound": ["return a00_r01.execute(other, lookup)"],
        }
        for name, lines in bad.items():
            ok, reason, _ = glue_gate(body(lines), CAT)
            self.assertFalse(ok, name)

    def test_payload_caps(self):
        long_str = "x" * 33
        ok, reason, _ = glue_gate(body([f"return a00_r01.execute(table, lookup, steps='{long_str}')"]), CAT)
        self.assertFalse(ok)
        self.assertIn("string constant", reason)
        many = ", ".join(f"c{i}='{'y' * 30}'" for i in range(5))      # 150 chars total
        ok, reason, _ = glue_gate(body([f"return a00_r01.execute(table, lookup, {many})"]), CAT)
        self.assertFalse(ok)
        self.assertIn("payload", reason)
        self.assertTrue(glue_gate(body(["return a00_r01.execute(table, lookup, col='revenue_cents', k=3)"]), CAT)[0])

    def test_rejects_imports_outside_library_and_long_glue(self):
        self.assertFalse(glue_gate("import os\n" + OKG, CAT)[0])
        self.assertFalse(glue_gate(OKG.replace("a01_r02", "a09_r09"), CAT)[0])
        self.assertFalse(glue_gate("from tools import a00_r01 as z\n" + body(["return z.execute(table, lookup)"]), CAT)[0])
        long = body(["x0 = a00_r01.execute(table, lookup)"] +
                    [f"x{i} = a00_r01.execute(x{i-1}, lookup)" for i in range(1, 14)] + ["return x13"])
        ok, reason, _ = glue_gate(long, CAT)
        self.assertFalse(ok)
        self.assertIn("lines", reason)


def tool_for(env, task, desc):
    """A tool that exactly implements `task` (built like StubModel's tools)."""
    sm = StubModel(0, env)
    names = sorted({n for n, _ in task.steps} | {d for n, _ in task.steps for d in sm.deps.get(n, [])})
    body = "".join(f"    table = {sm.fname[n]}(table, lookup, **{p!r})\n" for n, p in task.steps)
    return ("from __future__ import annotations\n" + sm.prelude + "\n\n" +
            "\n\n".join(sm.src[n] for n in names) +
            "\n\ndef execute(table, lookup, **params):\n" + body + "    return table\n")


class FreezeAndScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = MechEnv(ENV)
        cls.tmp = tempfile.mkdtemp()
        cls.soc = os.path.join(cls.tmp, "L0_s01")
        Society(RunConfig(arm="L0", seed=1, n_rounds=3), cls.env, StubModel(1, cls.env), cls.soc).run()

    def test_freeze_rule(self):
        out = os.path.join(tempfile.mkdtemp(), "lib")
        kept, acl, meta = freeze_library(self.soc, out)
        index = json.load(open(os.path.join(self.soc, "library", "index.json")))
        sigs = [tuple(index[k]["signature_signal"]) for k in meta["kept"]]
        self.assertEqual(len(sigs), len(set(sigs)))                      # deduped
        self.assertEqual(meta["n_built"], len(meta["kept"]) + len(meta["dropped_all_crash"])
                         + len(meta["dropped_duplicate"]))
        for k in meta["kept"]:                                           # earliest passing in group
            grp = [e for e in index.values() if tuple(e["signature_signal"]) == tuple(index[k]["signature_signal"])]
            passing = sorted((e for e in grp if (e.get("harness") or {}).get("passed")),
                             key=lambda e: (e["round"], e["id"]))
            if passing:
                self.assertEqual(k, passing[0]["id"])
        for t in set(meta["kept"]) | set(meta["dependency_only"]):
            self.assertTrue(os.path.exists(os.path.join(out, "tools", t + ".py")))

    def test_parametric_tool_kept(self):
        """msg #79.1: a generic filter(col, op, value) is all-ERR on P_signal
        (called without params) but verifies 'filter' and must be kept."""
        soc = os.path.join(tempfile.mkdtemp(), "L0_s01")
        shutil.copytree(self.soc, soc)
        lib = os.path.join(soc, "library")
        with open(os.path.join(lib, "index.json")) as f:
            index = json.load(f)
        with open(os.path.join(lib, "acl.json")) as f:
            acl = json.load(f)
        src = ("def execute(table, lookup, col, op, value):\n"
               "    ops = {'>': lambda a: a is not None and a > value,\n"
               "           '<': lambda a: a is not None and a < value,\n"
               "           '==': lambda a: a == value}\n"
               "    return [dict(r) for r in table if ops[op](r.get(col))]\n")
        for tid, rnd in (("a06_r98", 98), ("a05_r99", 99)):            # two duplicates
            with open(os.path.join(lib, "tools", tid + ".py"), "w") as f:
                f.write(src)
            acl[tid] = []
            index[tid] = {"id": tid, "author": 6, "round": rnd, "label": "filter", "description": "generic filter",
                          "target": None, "implements": ["filter"], "static_imports": [],
                          "harness": None, "signature_signal": ["ERR:RuntimeError"] * 8}
        with open(os.path.join(lib, "acl.json"), "w") as f:
            json.dump(acl, f)
        with open(os.path.join(lib, "index.json"), "w") as f:
            json.dump(index, f)
        _, _, meta = freeze_library(soc, os.path.join(tempfile.mkdtemp(), "lib"), self.env)
        self.assertEqual(meta["kept_parametric"], ["a06_r98"])          # earliest of the two
        self.assertIn("a05_r99", meta["dropped_duplicate"])
        self.assertGreater(meta["parametric_share"], 0)
        # without env (no verification) it would have been dropped: the old bug
        _, _, meta0 = freeze_library(soc, os.path.join(tempfile.mkdtemp(), "lib"), None)
        self.assertIn("a06_r98", meta0["dropped_all_crash"])

    def test_full_seal_and_shuffle(self):
        self.assertEqual(len(PUBLISHED_TEST_SEAL), 64)
        self.assertEqual(self.env.m.seal_hash(self.env.m.tasks(0, "test")), PUBLISHED_TEST_SEAL)
        kept = [{"id": f"a0{i}_r01", "author": i, "description": "d", "implements": []} for i in range(5)]
        t = self.env.m.tasks(0, "test")[3]
        src = lambda _: "def execute(table, lookup):\n    return table\n"
        t2 = self.env.m.tasks(0, "test")[7]
        p0, p0b, p1 = solver_prompt(t, kept, src, 0, 5), solver_prompt(t, kept, src, 0, 5), solver_prompt(t, kept, src, 1, 5)
        self.assertEqual(p0, p0b)
        self.assertNotEqual(p0, p1)                                      # reshuffled per attempt
        # v0.3.10 A': catalogue first, task last -> tasks share the whole prefix within an attempt
        q0 = solver_prompt(t2, kept, src, 0, 5)
        self.assertTrue(p0.endswith("TASK: " + t.spec))
        prefix = p0[:-len("TASK: " + t.spec)]
        self.assertEqual(q0[:len(prefix)], prefix)
        # shuffle depends on (society seed, attempt), not the arm or task: same position order
        # for a different library with the same sorted ids
        kept_b = [dict(e, description="other") for e in kept]
        ids = lambda p: [l.split()[0] for l in p.splitlines() if l.startswith("a0")]
        self.assertEqual(ids(p0), ids(solver_prompt(t2, kept_b, src, 0, 5)))

    def test_sampling_mismatch_refused(self):
        soc = tempfile.mkdtemp()
        with open(os.path.join(soc, "run_manifest.json"), "w") as f:
            json.dump({"model": "dep-a", "temperature": None,
                       "sampling": {"temperature_sent": False, "token_param": "max_completion_tokens",
                                    "param_adaptations": []}}, f)
        class M:
            name, send_temperature, token_param, param_mode = "dep-a", True, "max_tokens", "strict"
        with self.assertRaises(SystemExit):
            check_sampling(soc, M())
        M.send_temperature, M.token_param = False, "max_completion_tokens"
        check_sampling(soc, M())                                       # matches: no error
        M.name = "dep-b"
        with self.assertRaises(SystemExit):
            check_sampling(soc, M())

    def test_dev_diagnostic_never_touches_test(self):
        soc = os.path.join(tempfile.mkdtemp(), "L0_s01")
        shutil.copytree(self.soc, soc)
        real = self.env.m.tasks
        def guarded(seed, split, *a, **kw):
            if split == "test":
                raise AssertionError("dev diagnostic requested the test split")
            return real(seed, split, *a, **kw)
        self.env.m.tasks = guarded
        try:
            res = score_society(soc, self.env, StubSolver(), attempts=1, split="dev")
        finally:
            self.env.m.tasks = real
        self.assertNotIn("U", res)
        self.assertIn("_dev_task_scores", res)                           # in memory only, for pooling
        written = json.load(open(os.path.join(soc, "utility_dev", "utility.json")))
        self.assertFalse([k for k in written if k.startswith("U") or k.startswith("_")], written.keys())
        self.assertIsNotNone(res["gate_fail_rate"])
        self.assertIsInstance(res["gate_fail_reasons"], dict)
        # msg #96.1: no arm-labelled per-attempt correctness, and nothing to rebuild it from
        rows = [json.loads(l) for l in open(os.path.join(soc, "utility_dev", "solver_log.jsonl"))]
        self.assertTrue(rows)
        for r in rows:
            self.assertFalse({"passed", "verdict"} & set(r), r)
            if r["gate_ok"]:
                self.assertFalse({"response", "imported"} & set(r), r)
        tools = os.listdir(os.path.join(soc, "utility_dev", "frozen_library", "tools"))
        self.assertFalse([t for t in tools if t.startswith("solver_")], tools)
        acl = json.load(open(os.path.join(soc, "utility_dev", "frozen_library", "acl.json")))
        self.assertFalse([t for t in acl if t.startswith("solver_")])

    def test_score_requires_unseal(self):
        with self.assertRaises(SystemExit) as cm:
            umain(["--society", self.soc])
        self.assertIn("unseal", str(cm.exception))

    def test_score_end_to_end_with_positive_control(self):
        soc = os.path.join(tempfile.mkdtemp(), "L0_s01")
        shutil.copytree(self.soc, soc)
        # positive control: add a tool that exactly implements test task 0
        test0 = self.env.m.tasks(0, "test")[0]
        lib = os.path.join(soc, "library")
        index = json.load(open(os.path.join(lib, "index.json")))
        acl = json.load(open(os.path.join(lib, "acl.json")))
        tid = "a07_r99"
        src = tool_for(self.env, test0, "")
        open(os.path.join(lib, "tools", tid + ".py"), "w").write(src)
        from boidsnet.runner.sandbox import SandboxedTool
        acl[tid] = []
        json.dump(acl, open(os.path.join(lib, "acl.json"), "w"))
        sig = self.env.signature(SandboxedTool(lib, tid))
        index[tid] = {"id": tid, "author": 7, "round": 99, "label": "ctrl",
                      "description": "pipeline " + " -> ".join(n for n, _ in test0.steps),
                      "target": None, "implements": [], "static_imports": [],
                      "harness": {"passed": True}, "signature_signal": sig}
        json.dump(index, open(os.path.join(lib, "index.json"), "w"))
        res = score_society(soc, self.env, StubSolver(), attempts=2)
        self.assertTrue(0.0 <= res["U"] <= 1.0)
        self.assertTrue(res["test_seal"].startswith("25634f7783ff"))
        log = [json.loads(l) for l in open(os.path.join(soc, "utility", "solver_log.jsonl"))]
        first = [r for r in log if r["task"] == test0.id]
        self.assertTrue(all(r["gate_ok"] and r["passed"] for r in first), first[:1])
        self.assertEqual(len(log), res["n_tasks"] * 2)
        with self.assertRaises(SystemExit):
            score_society(soc, self.env, StubSolver(), attempts=1)          # no overwrite


class EngineeringTests(unittest.TestCase):
    """msg #96.3: a distinct, logged engineering path that never touches the test split."""

    def _eng_soc(self, adaptations):
        soc = os.path.join(tempfile.mkdtemp(), "ENG_L0_s9001")
        os.makedirs(soc)
        with open(os.path.join(soc, "run_manifest.json"), "w") as f:
            json.dump({"model": "dep-a", "engineering": True, "temperature": None,
                       "sampling": {"temperature_sent": False, "token_param": "max_completion_tokens",
                                    "param_adaptations": adaptations}}, f)
        return soc

    def test_engineering_dev_accepts_effective_adapted_block(self):
        class M:
            name, send_temperature, token_param, param_mode = "dep-a", False, "max_completion_tokens", "strict"
        soc = self._eng_soc(["drop temperature", "max_tokens -> max_completion_tokens"])
        check_sampling(soc, M(), "dev")                                  # effective block matches
        M.token_param = "max_tokens"
        with self.assertRaises(SystemExit):
            check_sampling(soc, M(), "dev")                              # still strict on the effective block

    def test_engineering_never_scored_on_test(self):
        class M:
            name, send_temperature, token_param, param_mode = "dep-a", False, "max_completion_tokens", "strict"
        with self.assertRaises(SystemExit):
            check_sampling(self._eng_soc([]), M(), "test")
        with self.assertRaises(SystemExit):
            check_sampling(self._eng_soc([]), StubSolver(), "test")

    def test_confirmatory_still_refuses_adaptations(self):
        soc = self._eng_soc(["drop temperature"])
        man = json.load(open(os.path.join(soc, "run_manifest.json")))
        man["engineering"] = False
        json.dump(man, open(os.path.join(soc, "run_manifest.json"), "w"))
        class M:
            name, send_temperature, token_param, param_mode = "dep-a", False, "max_completion_tokens", "strict"
        with self.assertRaises(SystemExit):
            check_sampling(soc, M(), "dev")

    def test_run_engineering_flags(self):
        from boidsnet.runner.run import main as rmain
        out = tempfile.mkdtemp()
        with self.assertRaises(SystemExit):
            rmain(["--arm", "L0", "--seed", "1", "--out", out, "--engineering", "--frozen", "x.json"])
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            rmain(["--arm", "L0", "--seed", "1", "--out", out, "--engineering", "--n-rounds", "1"])
        man = json.load(open(os.path.join(out, "ENG_L0_s01", "run_manifest.json")))
        self.assertTrue(man["engineering"])
        self.assertIn("pre-freeze", man["deviation"])
        from boidsnet.runner.batch import main as bmain
        with self.assertRaises(SystemExit):
            bmain(["--out", out, "--seeds", "1", "--engineering"])
        from boidsnet.runner.pilot import main as pmain
        with self.assertRaises(SystemExit):
            pmain(["--out", out, "--seed", "1", "--engineering"])


class IsolationGateTests(unittest.TestCase):
    def test_real_model_refused_without_os_isolation(self):
        from boidsnet.runner import sandbox
        from boidsnet.runner.run import main as rmain
        old_level, old_env = sandbox._LEVEL, os.environ.get("BOIDS_SANDBOX")
        sandbox._LEVEL, os.environ["BOIDS_SANDBOX"] = None, "hook-only"
        try:
            with self.assertRaises(SystemExit) as cm:
                rmain(["--arm", "L0", "--seed", "1", "--out", tempfile.mkdtemp(), "--engineering",
                       "--model", "some-deployment", "--allow-spend"])
            self.assertIn("isolation", str(cm.exception))
        finally:
            sandbox._LEVEL = old_level
            if old_env is None:
                os.environ.pop("BOIDS_SANDBOX", None)
            else:
                os.environ["BOIDS_SANDBOX"] = old_env


class SmokeTests(unittest.TestCase):
    def test_smoke_exact_protocol_coverage(self):
        from boidsnet.runner.smoke import main as smain, SMOKE
        import io, contextlib
        out = os.path.join(tempfile.mkdtemp(), "smoke")
        with contextlib.redirect_stdout(io.StringIO()):
            rep = smain(["--out", out])
        self.assertTrue(rep["PASS"], rep["coverage_problems"])
        self.assertEqual(set(rep["per_arm"]), {"E", "L0", "R0", "IM"})
        self.assertEqual(set(rep["dev_diagnostic"]["per_arm"]), {"E", "L0", "R0", "IM"})
        for arm, d in rep["dev_diagnostic"]["per_arm"].items():
            self.assertFalse([k for k in d if k.startswith("U")], arm)
        for arm in SMOKE["arms"]:
            self.assertFalse(os.path.exists(os.path.join(out, f"ENG_{arm}_s9001", "utility")))
        with self.assertRaises(SystemExit):                              # protocol-fixed knobs
            smain(["--out", os.path.join(tempfile.mkdtemp(), "s"), "--n-rounds", "10"])
        with self.assertRaises(SystemExit):
            smain(["--out", os.path.join(tempfile.mkdtemp(), "s"), "--unseal"])

    def test_coverage_detects_missing_arm_and_wrong_T(self):
        from boidsnet.runner.smoke import main as smain, check_coverage
        import io, contextlib
        out = os.path.join(tempfile.mkdtemp(), "smoke")
        with contextlib.redirect_stdout(io.StringIO()):
            smain(["--out", out])
        shutil.rmtree(os.path.join(out, "ENG_R0_s9001"))
        man_p = os.path.join(out, "ENG_E_s9001", "run_manifest.json")
        man = json.load(open(man_p)); man["n_rounds"] = 10; json.dump(man, open(man_p, "w"))
        problems, _ = check_coverage(out, False)
        self.assertTrue(any("society dirs" in p for p in problems), problems)
        self.assertTrue(any("n_rounds" in p for p in problems), problems)

    def test_smoke_gates_fail_without_dev(self):
        from boidsnet.runner.pilot import smoke_gates
        rows = {"E": {"missing_module_rate": 0.0, "parametric_candidate_rate": 0.0}}
        g = smoke_gates(rows, None)
        self.assertIsNone(g["gate_fail<=0.20_all_arms"])
        self.assertFalse(g["PASS"])


class SolverBudgetTests(unittest.TestCase):
    """msg #130: the smoke's dev diagnostic has a hard solver cost cap; U never does."""

    def test_dev_budget_stops_and_reports(self):
        env = MechEnv(ENV)
        soc = os.path.join(tempfile.mkdtemp(), "L0_s01")
        Society(RunConfig(arm="L0", seed=1, n_rounds=2), env, StubModel(1, env), soc).run()

        class Costly(StubSolver):
            def solve(self, task, kept, k):
                text, _, _ = super().solve(task, kept, k)
                return text, 900, 100                       # 1000 tokens per call
        r = score_society(soc, env, Costly(), attempts=1, split="dev", token_budget=2500)
        self.assertTrue(r["solver_truncated_by_budget"])
        self.assertEqual(r["n_tasks_scored"], 3)              # 0,1000,2000 < 2500 -> 3 calls, then stop
        self.assertEqual(r["solver_tokens"], 3000)
        self.assertEqual(r["solver_calls"], 3)

    def test_no_budget_on_confirmatory_u(self):
        env = MechEnv(ENV)
        with self.assertRaises(ValueError):
            score_society(tempfile.mkdtemp(), env, StubSolver(), split="test", token_budget=1000)


class PilotDevTests(unittest.TestCase):
    def test_pilot_score_dev_pools_u_dev(self):
        from boidsnet.runner.pilot import main as pmain
        from boidsnet.runner.utility import gate_reason_class
        out = tempfile.mkdtemp()
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            pmain(["--out", out, "--seed", "901", "--score-dev", "--n-rounds", "2"])
        rep = json.load(open(os.path.join(out, "pilot_report.json")))
        dev = rep["dev_diagnostic"]
        self.assertIn("U_dev_POOLED_DIAGNOSTIC", dev)
        for arm, d in dev["per_arm"].items():
            self.assertFalse([k for k in d if k.startswith("U")], arm)   # no per-arm U_dev
            self.assertIn("gate_fail_rate", d)
            self.assertIn("n_kept", d)
        self.assertIn("gate_fail<=0.20_all_arms", rep["smoke_gates"])
        self.assertIsNotNone(rep["l0_replicate"])                       # protocol §8: 2 L0 societies
        self.assertTrue(os.path.exists(os.path.join(out, "L0_s902", "rounds.jsonl")))
        self.assertEqual(rep["projected_solver_calls"], 10 * 6 * 60 * 3)
        self.assertEqual(gate_reason_class("a09_r09 is not in the library"), "import not in library")
        self.assertEqual(gate_reason_class("17 lines > 15"), "N lines > N")


if __name__ == "__main__":
    unittest.main()
