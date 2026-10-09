import json
import subprocess

import pytest

from ecology.images import resolve_image

IDENTITY = "sha256:" + "a" * 64


def test_tag_is_resolved_and_only_full_id_is_inspected(monkeypatch):
    commands = []

    def output(command, **kwargs):
        commands.append(command)
        if command[2] == "ls":
            return IDENTITY + "\n"
        assert command[-1] == IDENTITY
        return json.dumps([{"Id": IDENTITY}])

    monkeypatch.setattr(subprocess, "check_output", output)
    assert resolve_image("local:tag") == IDENTITY
    assert len(commands) == 2


@pytest.mark.parametrize("listed", ["", IDENTITY + "\nsha256:" + "b" * 64])
def test_absent_or_ambiguous_tag_is_not_guessed(monkeypatch, listed):
    monkeypatch.setattr(subprocess, "check_output", lambda *args, **kwargs: listed)
    with pytest.raises(RuntimeError, match="exactly one"):
        resolve_image("local:tag")


def test_full_id_inspection_must_match(monkeypatch):
    monkeypatch.setattr(subprocess, "check_output", lambda *args, **kwargs: '[{"Id":"other"}]')
    with pytest.raises(RuntimeError, match="disagrees"):
        resolve_image(IDENTITY)
