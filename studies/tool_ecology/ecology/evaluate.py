import json
import shutil
import subprocess
import uuid
from pathlib import Path

from .audit import SELECTED, VISIBLE
from .model import AgentPortModel
from .registry import Registry, file_hashes
from .sandbox import run_agent, stop


def parse_grade(logs: Path) -> dict:
    reward = logs / "reward.json"
    behavior = logs / "behavior.json"
    if not reward.is_file() or not behavior.is_file():
        raise RuntimeError("grader infrastructure failure: missing score/behavior result")
    score, counts = json.loads(reward.read_text()), json.loads(behavior.read_text())
    total, passed = counts.get("total", 0), counts.get("passed", 0)
    if not isinstance(total, int) or not isinstance(passed, int) or total <= 0 or not 0 <= passed <= total:
        raise RuntimeError("grader infrastructure failure: invalid/empty test counts")
    return dict(
        passed=passed,
        total=total,
        pass_rate=passed / total,
        strict_success=passed == total,
        ldb_score=score.get("reward"),
        raw_score=score,
        failure_class="none" if passed == total else "task_failure",
    )


def validate_grader_exit(returncode: int, data: dict):
    if returncode not in (0, 1) or (returncode != 0 and data["strict_success"]):
        raise RuntimeError(f"grader infrastructure failure: inconsistent exit {returncode}")


def grade(
    workspace: Path,
    library: Path,
    problem: Path,
    out: Path,
    image: str,
    *,
    ablate_edge="",
    timeout_seconds=240,
):
    out.mkdir(parents=True)
    logs, traces = out / "verifier", out / "traces"
    logs.mkdir()
    traces.mkdir()
    instrument = Path(__file__).resolve().parent / "instrument"
    container_name = f"boids-grader-{uuid.uuid4().hex[:12]}"
    # Tests are introduced only AFTER the model exits, in a different container.
    cmd = [
        "docker",
        "run",
        "--name",
        container_name,
        "--rm",
        "--network=none",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--memory=3g",
        "--cpus=2",
        "--pids-limit=256",
        "-w",
        "/workspace",
        "-v",
        f"{workspace.resolve()}:/workspace:rw",
        "-v",
        f"{library.resolve()}:/library:ro",
        "-v",
        f"{problem.resolve()}/tests:/tests:ro",
        "-v",
        f"{logs.resolve()}:/logs/verifier:rw",
        "-v",
        f"{traces.resolve()}:/trace:rw",
        "-v",
        f"{instrument}:/instrument:ro",
        "-e",
        "PYTHONPATH=/library:/instrument",
        "-e",
        "PYDA_VENV=/opt/venv",
        "-e",
        "UV_OFFLINE=1",
        "-e",
        f"BOIDS_ABLATE_EDGE={ablate_edge}",
        image,
        "bash",
        "/tests/test.sh",
    ]
    (out / "command.json").write_text(json.dumps(cmd, indent=2))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        (out / "timeout.json").write_text(json.dumps({"timeout_seconds": exc.timeout}))
        raise RuntimeError("grader infrastructure failure: timed out") from exc
    finally:
        cleanup = subprocess.run(
            ["docker", "rm", "-f", container_name], capture_output=True, text=True, timeout=20
        )
        (out / "cleanup.json").write_text(
            json.dumps({"returncode": cleanup.returncode, "stderr": cleanup.stderr}, indent=2)
        )
    (out / "stdout.txt").write_text(result.stdout)
    (out / "stderr.txt").write_text(result.stderr)
    data = parse_grade(logs)
    validate_grader_exit(result.returncode, data)
    data.update(grader_returncode=result.returncode, intervention=ablate_edge or None)
    edges = {}
    for p in traces.glob("*.json"):
        for edge, values in json.loads(p.read_text()).items():
            previous = edges.setdefault(edge, dict(calls=0, mutated=0, exceptions=0))
            for k in previous:
                previous[k] += values.get(k, 0)
    data["executed_python_edges"] = edges
    (out / "result.json").write_text(json.dumps(data, indent=2))
    return data


def evaluate(root: Path, tasks: Path, frozen: Path, image: str, budget, key: str, *, steps=12):
    Registry.verify_freeze(frozen)
    (root / "freeze-input.json").write_text((frozen / "freeze.json").read_text())
    rows = []
    for name in SELECTED:
        if name in VISIBLE["pyda"]:
            raise ValueError("design-visible problem cannot be held-out")
        problem = tasks / "pyda/evaluation" / name
        slot = root / name
        slot.mkdir(parents=True)
        workspace = slot / "workspace"
        shutil.copytree(problem / "workspace", workspace)
        instruction = (problem / "instruction.md").read_text()
        (slot / "problem-hashes.json").write_text(json.dumps(file_hashes(problem), indent=2))
        prompt = f"""Solve the following programming problem in /workspace.
{instruction}

Reusable native Python libraries, if any, are read-only under /library/published. Read /library/catalogue.json and individual README.md files; import with `from published.ID import ...`. PYTHONPATH=/library. Use a library when it helps; you may also implement adapters or solve directly. Do not modify the library. You have no access to hidden tests or reference solutions. Test against examples or your own cases and finish with the submit command. Installed Python dependencies are available; no network or extra packages.
"""
        (slot / "prompt.txt").write_text(prompt)
        model = AgentPortModel(key, budget, f"consumer/{root.parent.name}/{name}")
        agent, env = run_agent(model, workspace, frozen, slot / "trajectory.json", image, steps)
        try:
            execution = agent.run(prompt)
        finally:
            stop(env)
        pre_grade = file_hashes(workspace)
        (slot / "submitted-hashes.json").write_text(json.dumps(pre_grade, indent=2))
        (slot / "submitted").mkdir()
        # file_hashes rejects symlinks/special files before any privileged host copy.
        for p in workspace.rglob("*.py"):
            if "__pycache__" not in p.parts:
                dest = slot / "submitted" / p.relative_to(workspace)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(p, dest)
        result = grade(workspace, frozen, problem, slot / "grade", image)
        Registry.verify_freeze(frozen)
        result.update(problem=name, consumer_exit=execution.get("exit_status"))
        rows.append(result)
        print(
            json.dumps(
                dict(
                    consumer=root.parent.name,
                    problem=name,
                    passed=result["passed"],
                    total=result["total"],
                    calls=budget.calls,
                )
            ),
            flush=True,
        )
    (root / "results.json").write_text(json.dumps(rows, indent=2))
    return rows


def references(tasks: Path, root: Path, image: str):
    root.mkdir(parents=True)
    empty = root / "empty"
    empty.mkdir()
    result = []
    for name in SELECTED:
        problem = tasks / "pyda/evaluation" / name
        workspace = root / name / "workspace"
        shutil.copytree(problem / "workspace", workspace)
        shutil.copyfile(problem / "solution/no-library/main.py", workspace / "main.py")
        row = grade(workspace, empty, problem, root / name / "grade", image)
        row["problem"] = name
        result.append(row)
    (root / "results.json").write_text(json.dumps(result, indent=2))
    if not all(r["strict_success"] for r in result):
        raise RuntimeError("reference verification failed")
    return result
