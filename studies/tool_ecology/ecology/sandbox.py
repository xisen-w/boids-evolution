import os
import subprocess
from pathlib import Path

from minisweagent.agents.default import DefaultAgent
from minisweagent.environments.docker import DockerEnvironment

SYSTEM = "You are a software engineering agent. Use bash tools to inspect, edit and test your work. Every response must include a bash tool call."
INSTANCE = """{{task}}

Execution: each bash command starts a new subshell. Files persist. Offline Python and the installed dependencies are available. Use python for edits and tests. You have a bounded number of model steps: finish a small working contribution rather than an unfinished large one.
To finish, issue ONLY: echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT
"""


def run_agent(model, workspace: Path, library: Path, output: Path, image: str, steps: int):
    workspace.mkdir(parents=True, exist_ok=True)
    library.mkdir(parents=True, exist_ok=True)
    env = DockerEnvironment(
        image=image,
        cwd="/workspace",
        timeout=30,
        container_timeout="30m",
        # Login shells reset PATH to the system Python, hiding the pinned venv.
        interpreter=["bash", "-c"],
        env={
            "PYTHONPATH": "/library",
            "HOME": "/tmp",
            "PATH": "/opt/venv/bin:/usr/local/bin:/usr/bin:/bin",
            "VIRTUAL_ENV": "/opt/venv",
            "PYDA_VENV": "/opt/venv",
            "UV_OFFLINE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        run_args=[
            "--rm",
            "--user",
            f"{os.getuid()}:{os.getgid()}",
            "--network=none",
            "--read-only",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
            "--pids-limit=256",
            "--memory=2g",
            "--cpus=2",
            "--tmpfs=/tmp:rw,size=128m",
            "-v",
            f"{workspace.resolve()}:/workspace:rw",
            "-v",
            f"{library.resolve()}:/library:ro",
        ],
    )
    agent = DefaultAgent(
        model,
        env,
        system_template=SYSTEM,
        instance_template=INSTANCE,
        step_limit=steps,
        cost_limit=0,
        wall_time_limit_seconds=900,
        output_path=output,
    )
    return agent, env


def stop(env):
    if env.container_id:
        subprocess.run(["docker", "rm", "-f", env.container_id], capture_output=True, timeout=20, check=True)
        env.container_id = None
