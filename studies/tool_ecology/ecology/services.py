"""Docker evaluation of published service adapters. References stay on the host."""

import json
import subprocess
import uuid
from pathlib import Path

from . import workload
from .registry import Registry, safe_files


def judge(library, artifact, out, image, *, seed, round_, ablate_edge="", instrument=True):
    Registry.verify_freeze(library) if (library / "freeze.json").exists() else None
    out.mkdir(parents=True)
    traces = out / "traces"
    traces.mkdir()
    checks = artifact.get("checks", {})
    if set(checks) - set(workload.FAMILIES):
        raise ValueError("unknown workload family in checks")
    cases = []
    for family, function in sorted(checks.items()):
        for index, case in enumerate(workload.cases(seed, round_, family)):
            cases.append(dict(family=family, index=index, callable=function, **case))
    (out / "inputs.json").write_text(json.dumps(dict(identity=artifact["id"], cases=cases), indent=2))
    name = f"boids-service-{uuid.uuid4().hex[:12]}"
    instrument_path = Path(__file__).resolve().parent / "instrument"
    args = [
        "docker",
        "run",
        "--rm",
        "--name",
        name,
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--memory=1g",
        "--cpus=1",
        "--pids-limit=128",
        "--tmpfs=/tmp:rw,size=64m",
        "-v",
        f"{library.resolve()}:/library:ro",
        "-v",
        f"{out.resolve()}:/judge:ro",
        "-v",
        f"{traces.resolve()}:/trace:rw",
        "-v",
        f'{Path(__file__).with_name("service_worker.py")}:/worker.py:ro',
        "-v",
        f"{instrument_path}:/instrument:ro",
        "-e",
        "PYTHONPATH=/library:/instrument" if instrument else "PYTHONPATH=/library",
        "-e",
        "PYTHONDONTWRITEBYTECODE=1",
        "-e",
        f"BOIDS_ABLATE_EDGE={ablate_edge}",
        image,
        "python",
        "/worker.py",
    ]
    (out / "command.json").write_text(json.dumps(args, indent=2))
    try:
        completed = subprocess.run(args, capture_output=True, text=True, timeout=45)
    except subprocess.TimeoutExpired as exc:
        (out / "failure.json").write_text(json.dumps(dict(type="service_timeout", seconds=exc.timeout)))
        # Valid admitted untrusted programs can hang: capability failure, not successful service.
        completed = None
    finally:
        cleanup = subprocess.run(["docker", "rm", "-f", name], capture_output=True, text=True, timeout=20)
        (out / "cleanup.json").write_text(
            json.dumps(dict(returncode=cleanup.returncode, stderr=cleanup.stderr))
        )
    if completed:
        (out / "stdout.txt").write_text(completed.stdout[:100000])
        (out / "stderr.txt").write_text(completed.stderr[:100000])
    if completed and completed.returncode in (125, 126, 127):
        raise RuntimeError("service grader infrastructure failure: Docker did not start worker")
    try:
        safe = safe_files(traces)
        oversized = sum(p.stat().st_size for p in safe) > 2_000_000
        unsafe = None
    except ValueError as exc:
        oversized, unsafe = False, str(exc)
    output_file = traces / "outputs.json"
    contract_failure = oversized or unsafe is not None
    if contract_failure:
        (out / "output-contract-failure.json").write_text(
            json.dumps(dict(oversized=oversized, unsafe=unsafe))
        )
    outputs = json.loads(output_file.read_text()) if not contract_failure and output_file.exists() else []
    indexed = {(r["family"], r["index"]): r for r in outputs}
    families = {f: dict(passed=0, total=6, crashed=0, input_mutations=0) for f in checks}
    details = []
    for case in cases:
        actual = indexed.get((case["family"], case["index"]))
        stats = families[case["family"]]
        error = actual.get("error") if actual else "worker failed or timed out"
        mutated = actual.get("input_mutated", False) if actual else False
        expected = workload.reference(case["family"], case["rows"], case["lookup"], case["request"])
        correct = bool(
            actual and not error and not mutated and workload.equal(actual.get("output"), expected)
        )
        stats["passed"] += int(correct)
        stats["crashed"] += int(bool(error))
        stats["input_mutations"] += int(mutated)
        details.append(
            dict(
                family=case["family"],
                index=case["index"],
                correct=correct,
                error=error,
                input_mutated=mutated,
                executed_edges=actual.get("executed_edges", []) if actual else [],
            )
        )
    edges = {}
    for file in [] if contract_failure else traces.glob("*.json"):
        if file.name == "outputs.json":
            continue
        for edge, values in json.loads(file.read_text()).items():
            merged = edges.setdefault(edge, dict(calls=0, mutated=0, exceptions=0))
            for key in merged:
                merged[key] += values.get(key, 0)
    result = dict(
        identity=artifact["id"],
        families=families,
        details=details,
        edges=edges,
        intervention=ablate_edge or None,
        instrumented=instrument,
        returncode=completed.returncode if completed else None,
        failure_class=(
            "generated_output_contract_failure"
            if contract_failure
            else "generated_program_failure"
            if not completed or completed.returncode != 0
            else "service_task_failure"
            if any(s["passed"] != s["total"] for s in families.values())
            else "none"
        ),
    )
    (out / "result.json").write_text(json.dumps(result, indent=2))
    return result
