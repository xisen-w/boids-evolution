"""Host operations on an agent-owned workspace after its container stops."""

import json
import os
import shutil
import tempfile
from pathlib import Path

from .registry import safe_files


def remove_workspace_entry(path: Path):
    # A broken link is invisible to exists(), and rmtree must never follow a link.
    if path.is_symlink() or not path.is_dir():
        path.unlink(missing_ok=True)
    else:
        shutil.rmtree(path)


def archive_rejected(candidate: Path, destination: Path) -> dict:
    """Archive only a validated, bounded tree; never dereference a rejected root."""
    try:
        files = safe_files(candidate)
        if len(files) > 64 or sum(p.stat().st_size for p in files) > 300_000:
            raise ValueError("rejected archive exceeds file/byte limit")
    except (OSError, ValueError) as exc:
        return {"archived": False, "reason": str(exc)}
    destination.mkdir()
    for source in files:
        target = destination / source.relative_to(candidate)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return {"archived": True}


def write_feedback(workspace: Path, result: dict):
    """Replace the directory entry atomically, without following its old target."""
    fd, temporary = tempfile.mkstemp(prefix=".feedback-", dir=workspace)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(result, handle, indent=2)
        os.replace(temporary, workspace / "last_publication_feedback.json")
    finally:
        Path(temporary).unlink(missing_ok=True)
