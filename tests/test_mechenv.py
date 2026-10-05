"""Properties the protocol relies on: determinism, split disjointness, seal, harness sanity."""
import os
import subprocess
import sys
import unittest

from boidsnet.env import mechenv as m

# Candidate v0.2.2 seal after isolating final-test coverage input tables.
TEST_SEAL = "c9f634ae53c8f62694aed012f83520b53541175462552afdac5d1e40c93b7c0d"


class TestMechEnv(unittest.TestCase):
    def test_seal_hash_unchanged(self):
        self.assertEqual(m.seal_hash(m.tasks(0, "test")), TEST_SEAL)

    def test_seal_independent_of_hash_randomisation(self):
        # v0.2 drew from list(TERMINAL), a set, so the task list depended on
        # PYTHONHASHSEED (seed 5 gave a different sealed split). Fixed in v0.2.1.
        code = "from boidsnet.env import mechenv as m; print(m.seal_hash(m.tasks(0, 'test')))"
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for h in ("0", "1", "5", "7", "random"):
            out = subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True,
                                 text=True, env=dict(os.environ, PYTHONHASHSEED=h), check=True)
            self.assertEqual(out.stdout.strip(), TEST_SEAL, f"PYTHONHASHSEED={h}")

    def test_tasks_deterministic(self):
        a = [t.spec for t in m.tasks(0, "dev")]
        b = [t.spec for t in m.tasks(0, "dev")]
        self.assertEqual(a, b)

    def test_dev_seal_preserved_and_test_inputs_disjoint(self):
        dev, test = m.tasks(0, "dev"), m.tasks(0, "test")
        self.assertEqual(m.seal_hash(dev), "22cc39d56cd39ec426f890d78b5caf30860bcb4498b4c643fc7a00bafde7600c")
        for t in test:
            self.assertTrue(all(50000 <= s < 60000 for s in t.probe_seeds["coverage"]))
        for t in dev:
            self.assertTrue(all(30000 <= s < 40000 for s in t.probe_seeds["coverage"]))

    def test_seed_ranges_disjoint(self):
        spans = sorted(m.SEED_RANGES.values())
        for (_, hi), (lo, _) in zip(spans, spans[1:]):
            self.assertLessEqual(hi, lo)

    def test_reference_passes_and_identity_fails(self):
        task = m.tasks(0, "dev")[5]
        self.assertTrue(m.harness(task.reference, task).passed)
        self.assertFalse(m.harness(lambda t, lk: t, task).passed)

    def test_crashes_never_count_as_agreement(self):
        def boom(t, lk):
            raise ValueError
        v = m.behaviour_vector(boom, "signal")
        self.assertEqual(m.behaviour_similarity(v, v), 0.0)


if __name__ == "__main__":
    unittest.main()
