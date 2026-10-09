import hashlib
import json
from pathlib import Path

TASK_PIN = "a1f4e886063373d43e52b53b98492cf108f294e3"
VISIBLE = {
    "pyda": ["overlapping-logs", "customer-merge"],
    "python_validation": ["profile-patch", "trading-events"],
    "uglypie": ["page-cleaner", "kml-schema-import"],
}
SELECTED = ["weather-features", "scorer-lineage"]


def audit(tasks: Path, dest: Path):
    import subprocess

    head = subprocess.check_output(["git", "-C", str(tasks), "rev-parse", "HEAD"], text=True).strip()
    if head != TASK_PIN:
        raise ValueError("task pin mismatch")
    dirty = subprocess.check_output(
        ["git", "-C", str(tasks), "status", "--porcelain", "--untracked-files=all"], text=True
    )
    if dirty:
        raise ValueError("task checkout differs from pinned source")
    rows = []
    for task in VISIBLE:
        root = tasks / task
        instruction = (root / "design/instruction.md").read_text()
        problems = sorted(p.name for p in (root / "evaluation").iterdir() if p.is_dir())
        rows.append(
            dict(
                task=task,
                problems=len(problems),
                public_examples=VISIBLE[task],
                held_out=[p for p in problems if p not in VISIBLE[task]],
                specification_sha256=hashlib.sha256(instruction.encode()).hexdigest(),
                capability_bullets=sum(x.startswith("- ") for x in instruction.splitlines()[:30]),
            )
        )
    result = dict(
        task_revision=head,
        reviewed="three design specifications, environment requirements, task/problem inventory; not hidden test assertions",
        candidates=rows,
        selected_task="pyda",
        selected_problems=SELECTED,
        selected_reason="deterministic IO, relational, grouping and time capabilities; closest to existing tool-building substrate",
        excluded_reason={
            "python_validation": "schema/metaclass/generic API interactions make interface engineering an additional initial confound",
            "uglypie": "shared mutable tree and parser semantics make independently authored components harder to combine initially",
        },
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2))
    return result
