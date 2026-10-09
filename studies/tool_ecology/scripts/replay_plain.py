import argparse
import json
import shutil
import subprocess
import uuid
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("run", type=Path)
args = p.parse_args()
root = args.run.resolve()
rows = []
for arm in ["local-neutral", "local-boids", "no-library"]:
    for problem in ["weather-features", "scorer-lineage"]:
        slot = root / arm / "evaluation" / problem
        out = root / "diagnostics/plain" / arm / problem
        out.mkdir(parents=True)
        (out / "verifier").mkdir()
        (out / "traces").mkdir()
        workspace = out / "workspace"
        shutil.copytree(slot / "workspace", workspace)
        command = json.loads((slot / "grade/command.json").read_text())
        name = "boids-plain-" + uuid.uuid4().hex[:12]
        command[command.index("--name") + 1] = name
        for i, arg in enumerate(command):
            if arg.endswith(":/workspace:rw"):
                command[i] = str(workspace) + ":/workspace:rw"
            if arg.endswith(":/logs/verifier:rw"):
                command[i] = str(out / "verifier") + ":/logs/verifier:rw"
            if arg.endswith(":/trace:rw"):
                command[i] = str(out / "traces") + ":/trace:rw"
            if arg == "PYTHONPATH=/library:/instrument":
                command[i] = "PYTHONPATH=/library"
        (out / "command.json").write_text(json.dumps(command, indent=2))
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=240)
        finally:
            subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=20)
        (out / "stdout.txt").write_text(result.stdout)
        (out / "stderr.txt").write_text(result.stderr)
        counts = json.loads((out / "verifier/behavior.json").read_text())
        reward = json.loads((out / "verifier/reward.json").read_text())
        original = json.loads((slot / "grade/result.json").read_text())
        if result.returncode not in [0, 1] or counts["total"] <= 0:
            raise ValueError("plain grader infrastructure failure")
        row = dict(
            condition=arm,
            problem=problem,
            passed=counts["passed"],
            total=counts["total"],
            ldb_score=reward["reward"],
            same_test_counts=counts["passed"] == original["passed"] and counts["total"] == original["total"],
            same_ldb_score=abs(reward["reward"] - original["ldb_score"]) < 1e-12,
        )
        rows.append(row)
        print(json.dumps(row), flush=True)
(root / "diagnostics/plain-results.json").write_text(json.dumps(rows, indent=2))
if not all(r["same_test_counts"] and r["same_ldb_score"] for r in rows):
    raise ValueError("instrumentation sensitivity differs; preserve both")
