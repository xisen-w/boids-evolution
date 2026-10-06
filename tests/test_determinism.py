"""Hash-seed independence (msg #75): the same society under different
PYTHONHASHSEED values must produce byte-identical prompts and the same seal."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(hashseed, arm="R0"):
    out = tempfile.mkdtemp()
    env = dict(os.environ, PYTHONHASHSEED=str(hashseed))
    subprocess.run([sys.executable, "-m", "boidsnet.runner.run", "--arm", arm, "--seed", "3", "--out", out,
                    "--n-rounds", "3"], cwd=ROOT, env=env, check=True, capture_output=True)
    d = os.path.join(out, f"{arm}_s03")
    with open(os.path.join(d, "rounds.jsonl")) as fh:
        recs = [json.loads(l) for l in fh]
    return [(r["tool_id"], r["prompt_sha256"], r["menu"], r["exemplars"], r["neighbours"]) for r in recs]


class DeterminismTests(unittest.TestCase):
    def test_seal_independent_of_hash_seed(self):
        seals = set()
        for h in ("0", "5", "11"):
            code = ("import sys; from boidsnet.env import mechenv as m; "
                    "print(m.seal_hash(m.tasks(0, 'test')), m.seal_hash(m.tasks(0, 'dev')))")
            p = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True,
                               env=dict(os.environ, PYTHONHASHSEED=h), check=True)
            seals.add(p.stdout.strip())
        self.assertEqual(len(seals), 1, seals)
        self.assertTrue(next(iter(seals)).startswith("25634f77"))

    def test_society_independent_of_hash_seed(self):
        for arm in ("R0", "G0m"):
            self.assertEqual(run(0, arm), run(5, arm), arm)


if __name__ == "__main__":
    unittest.main()
