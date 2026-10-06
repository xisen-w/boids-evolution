"""Freeze: hash the runner source and the protocol text.

    python -m boidsnet.runner.freeze --protocol joint_thesis_protocol.md > FROZEN.json

Post FROZEN.json (not the code) to the room before any paid run; run.py
refuses a paid run whose source hash differs.
"""
import argparse
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def code_hash(env_path=None):
    """sha256 over the runner source and the env file actually used."""
    env_path = env_path or os.path.join(os.path.dirname(HERE), "env", "mechenv.py")
    h = hashlib.sha256()
    for name in sorted(os.listdir(HERE)):
        if name.endswith(".py"):
            h.update(name.encode())
            with open(os.path.join(HERE, name), "rb") as f:
                h.update(f.read())
    h.update(b"env")
    with open(env_path, "rb") as f:
        h.update(f.read())
    runtime = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docker", "tool-sandbox")
    for name in ("Dockerfile", "build_runtime.py"):
        h.update(("docker/tool-sandbox/" + name).encode())
        with open(os.path.join(runtime, name), "rb") as f:
            h.update(f.read())
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--protocol", required=True)
    a = p.parse_args()
    with open(a.protocol, "rb") as f:
        proto = hashlib.sha256(f.read()).hexdigest()
    print(json.dumps({"code_sha256": code_hash(), "protocol_sha256": proto}, indent=1))


if __name__ == "__main__":
    main()
