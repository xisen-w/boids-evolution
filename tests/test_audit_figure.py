import csv
import hashlib
import importlib.util
import os
import tempfile
import unittest

try:
    import matplotlib  # noqa: F401
    HAVE_MPL = True
except ImportError:
    HAVE_MPL = False

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "scripts", "audit_tci_figure.py")


def load_module():
    spec = importlib.util.spec_from_file_location("audit_tci_figure", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@unittest.skipUnless(HAVE_MPL, "matplotlib not installed")
class AuditFigureTest(unittest.TestCase):
    def test_reconstructs_published_round1_alignment(self):
        # Round 1 of alignment_4.1: 15 created tools at 4.94 plus 8 seeds at 1.48 -> 3.737.
        m = load_module()
        rows = [{"domain": "data_science", "arm": "alignment_4.1", "run_id": "r", "dup_group": "",
                 "round": 1, "is_seed": s, "tci": v}
                for s, v, k in ((False, 4.94, 15), (True, 1.48, 8)) for _ in range(k)]
        pub, new = m.series(rows)
        self.assertAlmostEqual(pub[0], (15 * 4.94 + 8 * 1.48) / 23, places=9)
        self.assertEqual(round(pub[0], 3), 3.737)
        self.assertAlmostEqual(new[0], 4.94, places=9)

    def test_duplicate_group_drawn_once_and_png_deterministic(self):
        m = load_module()
        d = tempfile.mkdtemp()
        path = os.path.join(d, "x.csv")
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["domain", "arm", "run_id", "dup_group", "round", "is_seed", "tci"])
            for run, dom, grp in (("a", "data_science", "g1"), ("b", "literature", "g1"),
                                  ("c", "literature", "")):
                for t in range(1, 16):
                    w.writerow([dom, "baseline_4.1", run, grp, t, 0, 5 + 0.01 * t])
        rows = m.load(path)
        kept, n_dirs, n_groups = m.dedupe(rows)
        self.assertEqual((n_dirs, n_groups), (3, 1))
        self.assertEqual(sorted({r["run_id"] for r in kept}), ["a", "c"])
        h = []
        for i in range(2):
            out = os.path.join(d, f"o{i}.png")
            m.plot(rows, out)
            with open(out, "rb") as f:
                h.append(hashlib.sha256(f.read()).hexdigest())
        self.assertEqual(h[0], h[1])


if __name__ == "__main__":
    unittest.main()
