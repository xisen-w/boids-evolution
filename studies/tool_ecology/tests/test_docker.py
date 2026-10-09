import json
import os
import subprocess

import pytest
from minisweagent.models.test_models import DeterministicModel, make_output

from ecology.images import resolve_image
from ecology.registry import Registry
from ecology.sandbox import run_agent, stop


def test_real_mini_agent_edits_tests_repairs_and_isolation(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fixture-secret-must-stay-on-host")
    image = resolve_image("boids-pyda:20261008")
    workspace, library = tmp_path / "private", tmp_path / "view"
    library.mkdir()
    (library / "readonly.txt").write_text("visible")
    first = """python - <<'PY'
import os, pathlib, socket, sys
import numpy, pyarrow, dateutil
assert sys.prefix == '/opt/venv', (sys.executable, sys.prefix)
assert pyarrow.__version__ == '18.1.0'
assert numpy.__version__ == '2.2.6'
assert not any(k in os.environ for k in ('OPENAI_API_KEY', 'AGENTPORT_API_KEY', 'ANTHROPIC_API_KEY', 'AZURE_OPENAI_API_KEY'))
assert 'fixture-secret-must-stay-on-host' not in os.environ.values()
assert not pathlib.Path('/tests').exists()
assert not pathlib.Path('/registry').exists()
assert not pathlib.Path('/var/run/docker.sock').exists()
try:
 pathlib.Path('/library/readonly.txt').write_text('oops')
 raise AssertionError('library writable')
except OSError: pass
s=socket.socket(); s.settimeout(1)
assert s.connect_ex(('1.1.1.1',443)) != 0
print('ISOLATION_AND_DEPENDENCIES_VERIFIED', flush=True)
pathlib.Path('answer.py').write_text('def answer(): return 2\\n')
from answer import answer
assert answer() == 3, 'INTENTIONAL_ANSWER_MISMATCH'
PY"""
    second = """python - <<'PY'
from pathlib import Path
Path('answer.py').write_text('def answer(): return 3\\n')
from answer import answer
assert answer() == 3
print('REPAIR_VERIFIED')
PY"""
    model = DeterministicModel(
        outputs=[
            make_output("", [{"command": cmd}], 0)
            for cmd in [first, second, "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"]
        ]
    )
    agent, env = run_agent(model, workspace, library, tmp_path / "trajectory.json", image, 4)
    try:
        result = agent.run("Engineering fixture: edit/test/repair.")
    finally:
        stop(env)
    assert result["exit_status"] == "Submitted"
    outputs = [m["extra"]["returncode"] for m in agent.messages if "returncode" in m.get("extra", {})]
    assert outputs == [1, 0]
    first_output = next(
        m["extra"]["raw_output"] for m in agent.messages if "returncode" in m.get("extra", {})
    )
    assert "ISOLATION_AND_DEPENDENCIES_VERIFIED" in first_output
    assert "INTENTIONAL_ANSWER_MISMATCH" in first_output
    assert agent.n_calls == 3


def test_executed_cross_author_dependency_and_noncrashing_intervention(tmp_path):
    from test_registry import candidate

    reg = Registry(tmp_path / "registry")
    one = reg.publish("a00", 1, candidate(tmp_path, "one"), allowed=set())
    two = reg.publish(
        "a01",
        2,
        candidate(
            tmp_path, "two", [one], f"from published.{one} import value\ndef result(): return value()+1\n"
        ),
        allowed={one},
    )
    frozen = reg.freeze(tmp_path / "frozen")
    traces = tmp_path / "traces"
    traces.mkdir()
    from pathlib import Path

    instrument = Path(__file__).resolve().parents[1] / "ecology/instrument"
    edge = f"published.{two}->published.{one}.value"
    image = resolve_image("boids-pyda:20261008")

    def run(ablate):
        cmd = [
            "docker",
            "run",
            "--rm",
            "--user",
            f"{os.getuid()}:{os.getgid()}",
            "--network=none",
            "--read-only",
            "--cap-drop=ALL",
            "-v",
            f"{frozen}:/library:ro",
            "-v",
            f"{instrument}:/instrument:ro",
            "-v",
            f"{traces}:/trace:rw",
            "-e",
            "PYTHONPATH=/library:/instrument",
            "-e",
            f"BOIDS_ABLATE_EDGE={ablate}",
            image,
            "python",
            "-c",
            f"from published.{two} import result; print(result())",
        ]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20)

    baseline, intervention = run(""), run(edge)
    assert baseline.returncode == intervention.returncode == 0
    assert baseline.stdout.strip() == "4"
    assert intervention.stdout.strip() == "1"
    assert any(json.loads(p.read_text()).get(edge, {}).get("mutated") for p in traces.glob("*.json"))


def test_real_timed_out_grader_container_is_removed(tmp_path):
    from ecology.evaluate import grade

    workspace, library, problem = (tmp_path / name for name in ("workspace", "library", "problem"))
    workspace.mkdir()
    library.mkdir()
    (problem / "tests").mkdir(parents=True)
    (problem / "tests/test.sh").write_text("#!/bin/bash\nsleep 30\n")
    output = tmp_path / "grade"
    with pytest.raises(RuntimeError, match="infrastructure failure: timed out"):
        grade(workspace, library, problem, output, resolve_image("boids-pyda:20261008"), timeout_seconds=2)
    command = json.loads((output / "command.json").read_text())
    name = command[command.index("--name") + 1]
    remaining = subprocess.check_output(["docker", "ps", "-aq", "--filter", f"name=^{name}$"], text=True)
    assert not remaining.strip()
