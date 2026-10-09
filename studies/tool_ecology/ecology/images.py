import json
import re
import subprocess


def resolve_image(reference: str) -> str:
    """Resolve one local image and verify its full ID before creating containers."""
    identity = reference
    if not reference.startswith("sha256:"):
        # This daemon can list a local tag while inspect(tag) incorrectly says absent.
        identities = set(
            subprocess.check_output(
                ["docker", "image", "ls", "--no-trunc", "--quiet", reference], text=True
            ).split()
        )
        if len(identities) != 1:
            raise RuntimeError("image reference must resolve to exactly one local image")
        identity = identities.pop()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", identity):
        raise RuntimeError("image resolution did not return a full SHA256 ID")
    details = json.loads(subprocess.check_output(["docker", "image", "inspect", identity], text=True))
    if len(details) != 1 or details[0].get("Id") != identity:
        raise RuntimeError("image inspection disagrees with resolved ID")
    return identity
