"""Batch runner: completeness, resume, failed-dir handling."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from boidsnet.runner.batch import run_one, parse_seeds, main as batch_main


class BatchTests(unittest.TestCase):
    def test_parse_seeds(self):
        self.assertEqual(parse_seeds("1001-1003,1007"), [1001, 1002, 1003, 1007])

    def test_batch_resume_and_failed_rerun(self):
        out = tempfile.mkdtemp()
        with self.assertRaises(SystemExit) as cm:
            batch_main(["--out", out, "--seeds", "5-6", "--arms", "L0,IM", "--jobs", "2", "--n-rounds", "2"])
        self.assertEqual(cm.exception.code, 0)
        st = json.load(open(os.path.join(out, "batch_status.json")))
        self.assertEqual(st["ok"], 4)
        # resume: completed societies are skipped, not rerun
        r = run_one(out, "L0", 5, ["--n-rounds", "2"])
        self.assertEqual(r["attempts"], ["skipped_existing"])
        # a FAILED society is moved aside (kept) and rerun once
        d = os.path.join(out, "IM_s07")
        os.makedirs(d)
        json.dump({"error_type": "X"}, open(os.path.join(d, "FAILED.json"), "w"))
        r = run_one(out, "IM", 7, ["--n-rounds", "2"])
        self.assertEqual(r["status"], "OK")
        self.assertTrue(os.path.exists(d + ".failed1/FAILED.json"))
        self.assertTrue(os.path.exists(os.path.join(d, "summary.json")))


if __name__ == "__main__":
    unittest.main()
