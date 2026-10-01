"""Properties the protocol relies on: determinism, split disjointness, seal, harness sanity."""
import os
import subprocess
import sys
import unittest

from boidsnet.env import mechenv as m

# sealed TEST-split hash posted in the room (mechenv v0.2, tasks(0, "test"))
TEST_SEAL = "25634f7783fffbac3c2e1f74c545c2f647806218173b1af2dd3e2f1393c82371"


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
