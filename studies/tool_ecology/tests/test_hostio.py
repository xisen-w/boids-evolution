import json

from ecology.hostio import archive_rejected, remove_workspace_entry, write_feedback


def test_rejected_root_or_child_link_never_copies_host_contents(tmp_path):
    outside = tmp_path / "host-only"
    outside.mkdir()
    (outside / "secret").write_text("host-only-content")
    candidate = tmp_path / "candidate"
    candidate.symlink_to(outside, target_is_directory=True)
    destination = tmp_path / "archive"
    assert not archive_rejected(candidate, destination)["archived"]
    assert not destination.exists()
    remove_workspace_entry(candidate)
    assert (outside / "secret").read_text() == "host-only-content"
    candidate.mkdir()
    (candidate / "link").symlink_to(outside)
    assert not archive_rejected(candidate, destination)["archived"]
    assert not destination.exists()


def test_feedback_replaces_link_without_overwriting_its_host_target(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "host-file"
    outside.write_text("untouched")
    feedback = workspace / "last_publication_feedback.json"
    feedback.symlink_to(outside)
    write_feedback(workspace, {"publication_status": "published"})
    assert not feedback.is_symlink()
    assert json.loads(feedback.read_text())["publication_status"] == "published"
    assert outside.read_text() == "untouched"
    assert not list(workspace.glob(".feedback-*"))


def test_safe_rejection_is_archived_and_broken_candidate_removed(tmp_path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "partial.py").write_text("this is incomplete (")
    destination = tmp_path / "archive"
    assert archive_rejected(candidate, destination)["archived"]
    assert (destination / "partial.py").read_text() == "this is incomplete ("
    remove_workspace_entry(candidate)
    candidate.symlink_to(tmp_path / "missing")
    remove_workspace_entry(candidate)
    assert not candidate.is_symlink()
