import pytest

from ecology.evaluate import parse_grade
from ecology.model import Budget


def test_grader_missing_empty_and_failed_are_distinct(tmp_path):
    with pytest.raises(RuntimeError, match="missing"):
        parse_grade(tmp_path)
    (tmp_path / "reward.json").write_text('{"reward":0}')
    (tmp_path / "behavior.json").write_text('{"passed":0,"total":0}')
    with pytest.raises(RuntimeError, match="empty"):
        parse_grade(tmp_path)
    (tmp_path / "behavior.json").write_text('{"passed":1,"total":3}')
    assert parse_grade(tmp_path)["failure_class"] == "task_failure"


def test_physical_budget_reserved_before_request_and_not_reused(tmp_path):
    budget = Budget(tmp_path, call_limit=1)
    budget.reserve({"max_output_tokens": 10}, "test")
    assert (tmp_path / "request-0001.json").exists()
    with pytest.raises(RuntimeError):
        budget.reserve({"max_output_tokens": 10}, "test")
    with pytest.raises(ValueError):
        Budget(tmp_path)


def test_partial_passing_counts_cannot_override_failed_grader():
    from ecology.evaluate import validate_grader_exit

    for code in (1, 2, 125, 137):
        with pytest.raises(RuntimeError, match="inconsistent"):
            validate_grader_exit(code, {"strict_success": True})
    validate_grader_exit(1, {"strict_success": False})


def test_azure_reasoning_replay_removes_output_only_and_null_fields():
    from ecology.model import normalize_input

    original = [
        {
            "type": "reasoning",
            "id": "rs_1",
            "summary": [],
            "status": None,
            "content": None,
            "encrypted_content": None,
        },
        {
            "type": "function_call",
            "id": "fc_1",
            "call_id": "call_1",
            "name": "bash",
            "arguments": "{}",
            "status": "completed",
            "namespace": None,
        },
    ]
    assert normalize_input(original) == [
        {"type": "reasoning", "id": "rs_1", "summary": []},
        {"type": "function_call", "call_id": "call_1", "name": "bash", "arguments": "{}"},
    ]


def test_timed_out_grader_is_removed_and_classified_as_infrastructure(tmp_path, monkeypatch):
    import subprocess

    from ecology.evaluate import grade

    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        if command[:2] == ["docker", "run"]:
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="infrastructure failure: timed out"):
        grade(tmp_path / "workspace", tmp_path / "library", tmp_path / "problem", tmp_path / "grade", "image")
    name = commands[0][commands[0].index("--name") + 1]
    assert commands[1] == ["docker", "rm", "-f", name]
    assert (tmp_path / "grade/timeout.json").exists()
    assert not (tmp_path / "grade/result.json").exists()
