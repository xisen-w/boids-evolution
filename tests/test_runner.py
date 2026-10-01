"""Protocol-property tests.  Run: python -m unittest discover -s tests -v"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from boidsnet.runner.config import RunConfig
from boidsnet.runner.env_adapter import MechEnv
from boidsnet.runner.exposure import FRAMING, EXEMPLAR_CHARS, summarise
from boidsnet.runner.model import StubModel
from boidsnet.runner.run import main as run_main
from boidsnet.runner.sandbox import run_tool
from boidsnet.runner.society import Society


ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "boidsnet", "env", "mechenv.py")


def sealed_env():
    env = MechEnv(ENV_PATH)
    real = env.m.tasks

    def guarded(seed, split, *a, **kw):
        if split != "dev":
            raise AssertionError(f"runner requested split {split!r}")
        return real(seed, split, *a, **kw)
    env.m.tasks = guarded
    return env


def run_society(arm, seed=7, rounds=4, root=None):
    out = os.path.join(root, f"{arm}_{seed}")
    cfg = RunConfig(arm=arm, seed=seed, n_rounds=rounds)
    env = sealed_env()
    Society(cfg, env, StubModel(seed, env), out).run()
    with open(os.path.join(out, "rounds.jsonl")) as fh:
        recs = [json.loads(l) for l in fh]
    return out, recs


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.runs = {a: run_society(a, root=cls.tmp) for a in ("E", "L0", "L1", "G0", "R0", "G0m", "IM")}

    def test_framing_length_matched(self):
        lens = [len(v) for v in FRAMING.values()]
        self.assertLessEqual(max(lens) - min(lens), 3, lens)

    def test_content_fixed_across_local_arms(self):
        # The stub ignores framing, so histories coincide and any difference
        # in exemplars would come from the arm changing selection.
        key = lambda recs: [(r["round"], r["agent"], r["exemplars"]) for r in recs]
        e = key(self.runs["E"][1])
        self.assertEqual(e, key(self.runs["L0"][1]))
        self.assertEqual(e, key(self.runs["L1"][1]))

    def test_local_exemplars_come_from_ring_neighbours(self):
        for r in self.runs["L0"][1]:
            self.assertTrue(set(r["exemplar_authors"]) <= set(r["neighbours"]), r)

    def test_global_pool_is_society_wide(self):
        later = [r for r in self.runs["G0"][1] if r["round"] >= 2]
        self.assertTrue(all(r["pool_size"] == (r["round"] - 1) * 7 for r in later))

    def test_rule_fired_flags(self):
        for arm, expect in (("E", False), ("IM", False)):
            self.assertFalse(any(r["rule_fired"] for r in self.runs[arm][1]), arm)
        for arm in ("L0", "L1", "G0", "G0m"):
            fired = [r["rule_fired"] for r in self.runs[arm][1]]
            self.assertTrue(all(f == (r["round"] > 1) for f, r in zip(fired, self.runs[arm][1])))

    def test_im_has_no_social_channel(self):
        for r in self.runs["IM"][1]:
            self.assertEqual(r["exemplars"], [])
            self.assertEqual(r["cross_agent_imports"], [])
            self.assertEqual(r["catalogue_size"], r["round"] - 1)

    def test_synchronous_rounds(self):
        for arm, (_, recs) in self.runs.items():
            for r in recs:
                for t in r["exemplars"] + r.get("cross_agent_imports", []):
                    self.assertLess(int(t.split("_r")[1]), r["round"], (arm, r["tool_id"], t))

    def test_no_overwrite_unique_ids(self):
        out, recs = self.runs["L0"]
        files = [f for f in os.listdir(os.path.join(out, "library", "tools")) if f.startswith("a")]
        self.assertEqual(len(files), sum(r["parse_ok"] for r in recs))
        self.assertEqual(len({r["tool_id"] for r in recs}), len(recs))

    def test_failed_tools_are_listed_immediately(self):
        out, recs = self.runs["E"]
        last = max(r["round"] for r in recs)
        failed = [r for r in recs if r["round"] < last and not r["harness"]["passed"]]
        self.assertTrue(failed, "stub produced no failing tool; change seed")
        for f in failed:
            nxt = [r for r in recs if r["round"] == f["round"] + 1]
            for r in nxt:
                with open(os.path.join(out, "prompts", r["tool_id"] + ".json")) as fh:
                    self.assertIn(f"- {f['tool_id']} ", json.load(fh)["user"])

    def test_sandbox_hides_api_keys(self):
        lib = tempfile.mkdtemp()
        os.makedirs(os.path.join(lib, "tools"))
        open(os.path.join(lib, "tools", "__init__.py"), "w").close()
        with open(os.path.join(lib, "tools", "leak.py"), "w") as f:
            f.write("import os\ndef execute(x):\n    return os.environ.get('FAKE_API_KEY')\n")
        os.environ["FAKE_API_KEY"] = "secret"
        try:
            self.assertEqual(run_tool(lib, "leak", [{"args": [0]}]), [None])
        finally:
            del os.environ["FAKE_API_KEY"]

    def test_env_not_importable_by_tools(self):
        lib = tempfile.mkdtemp()
        os.makedirs(os.path.join(lib, "tools"))
        open(os.path.join(lib, "tools", "__init__.py"), "w").close()
        with open(os.path.join(lib, "tools", "cheat.py"), "w") as f:
            f.write("def execute(x):\n    import mechenv\n    return 1\n")
        out = run_tool(lib, "cheat", [{"args": [0]}])
        self.assertIn("ModuleNotFoundError", out[0]["__error__"])

    def test_signature_is_per_probe_and_harness_matches_reference(self):
        env = sealed_env()
        recs = self.runs["E"][1]
        passed = [r for r in recs if r["harness"]["passed"]]
        self.assertTrue(passed)
        for r in recs:
            self.assertEqual(len(r["signature_signal"]), len(env.signal_seeds))

    def test_task_menu_identical_across_arms(self):
        key = lambda recs: [(r["round"], r["agent"], r["menu"]) for r in recs]
        base = key(self.runs["E"][1])
        for arm in ("L0", "L1", "G0", "IM"):
            self.assertEqual(base, key(self.runs[arm][1]), arm)
        self.assertTrue(all(len(r["menu"]) == 8 for r in self.runs["E"][1]))

    def test_exemplar_summary_capped_and_no_source(self):
        long_doc = "x " * 1000
        src = f'def execute(table, lookup, **params):\n    """{long_doc}"""\n    SECRET_BODY = 1\n'
        e = {"id": "a01_r01", "author": 1, "description": "d", "implements": ["sort"]}
        text = summarise(e, src)
        self.assertLessEqual(len(text), EXEMPLAR_CHARS)
        self.assertNotIn("SECRET_BODY", text)
        out, recs = self.runs["L0"]
        for r in recs:
            if r["block_nonempty"]:
                with open(os.path.join(out, "prompts", r["tool_id"] + ".json")) as fh:
                    self.assertNotIn("def _copy", json.load(fh)["user"])

    def test_crashed_tools_are_never_similar(self):
        env = sealed_env()
        self.assertEqual(env.similarity(["ERR:X"] * 8, ["ERR:X"] * 8), 0.0)
        self.assertEqual(env.similarity(["a"] * 8, ["a"] * 8), 1.0)

    def test_exec_feedback_shown_to_author_only_next_round(self):
        out, recs = self.runs["L0"]
        by_id = {r["tool_id"]: r for r in recs}
        for r in recs:
            fb = r["exec_feedback_shown"]
            if r["round"] == 1:
                self.assertIsNone(fb)
                continue
            prev = by_id[fb["tool_id"]]
            self.assertEqual(prev["agent"], r["agent"])
            self.assertEqual(prev["round"], r["round"] - 1)
            self.assertNotIn("passed", fb["text"].lower())
            with open(os.path.join(out, "prompts", r["tool_id"] + ".json")) as fh:
                self.assertIn(fb["text"], json.load(fh)["user"])

    def test_exec_feedback_identical_across_local_arms(self):
        key = lambda recs: [(r["tool_id"], r["exec_feedback"]) for r in recs]
        self.assertEqual(key(self.runs["E"][1]), key(self.runs["L0"][1]))

    def test_random_neighbourhood_matches_local_pool_size(self):
        l0 = {(r["round"], r["agent"]): r for r in self.runs["L0"][1]}
        changed = 0
        for r in self.runs["R0"][1]:
            self.assertEqual(len(r["neighbours"]), 2)
            self.assertNotIn(r["agent"], r["neighbours"])
            self.assertEqual(r["pool_size"], l0[(r["round"], r["agent"])]["pool_size"])
            self.assertTrue(set(r["exemplar_authors"]) <= set(r["neighbours"]))
            changed += r["neighbours"] != l0[(r["round"], r["agent"])]["neighbours"]
        self.assertGreater(changed, 0)

    def test_g0m_matched_non_neighbours(self):
        recs = self.runs["G0m"][1]
        matched = [r for r in recs if r["selection_mode"].startswith("matched")]
        self.assertTrue(matched)
        for r in recs:
            self.assertFalse(set(r["exemplar_authors"]) & set(r["neighbours"]), r["tool_id"])
            self.assertNotIn(r["agent"], r["exemplar_authors"])
            self.assertEqual(len(r["exemplar_age"]), len(r["exemplars"]))
            self.assertEqual(len(r["exemplar_passed"]), len(r["exemplars"]))
        for r in matched:
            mt = r["exemplar_match"]
            self.assertEqual(len(mt["abs_diff"]), len(r["exemplars"]))
            self.assertEqual(mt["shortfall"], len(mt["targets"]) - len(r["exemplars"]))
            # the chosen tool is the closest available to each target
            for sv, t, d in zip(r["exemplar_similarity"], mt["targets"], mt["abs_diff"]):
                self.assertAlmostEqual(abs(sv - t), d, places=5)

    def test_g0m_exposure_schedule_matches_l0(self):
        l0 = {(r["round"], r["agent"]): r for r in self.runs["L0"][1]}
        for r in self.runs["G0m"][1]:
            o = l0[(r["round"], r["agent"])]
            self.assertEqual(r["neighbours"], o["neighbours"])
            self.assertEqual(len(r["exemplars"]), len(o["exemplars"]), r["tool_id"])

    def test_g0m_uses_only_its_own_society(self):
        tmp = tempfile.mkdtemp()
        out, recs = run_society("G0m", seed=11, root=tmp)
        self.assertEqual(os.listdir(tmp), [os.path.basename(out)])
        self.assertTrue(any(r["exemplars"] for r in recs))

    def test_paid_run_refused_without_freeze(self):
        with self.assertRaises(SystemExit) as cm:
            run_main(["--arm", "L0", "--seed", "1", "--out", self.tmp, "--model", "gpt-x"])
        self.assertIn("frozen", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
