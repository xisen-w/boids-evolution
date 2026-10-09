import argparse
import json
import subprocess
import uuid
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("run", type=Path)
args = p.parse_args()
root = args.run.resolve()
image = json.loads((root / "manifest.json").read_text())["image"]
rows = []
for arm in ["local-neutral", "local-boids"]:
    library = root / arm / "frozen"
    modules = [x["id"] for x in json.loads((library / "catalogue.json").read_text())]
    code = "import importlib,json,sys,pyarrow; rows=[]\n"
    code += (
        "for name in "
        + repr(modules)
        + ":\n try: importlib.import_module('published.'+name); rows.append({'id':name,'import_ok':True})\n except Exception as exc: rows.append({'id':name,'import_ok':False,'error':repr(exc)})\n"
    )
    code += "print(json.dumps({'python_prefix':sys.prefix,'pyarrow':pyarrow.__version__,'modules':rows}))"
    name = "boids-import-" + uuid.uuid4().hex[:12]
    command = [
        "docker",
        "run",
        "--name",
        name,
        "--rm",
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--pids-limit=256",
        "--memory=2g",
        "--cpus=2",
        "--tmpfs=/tmp:rw,size=128m",
        "-v",
        str(library) + ":/library:ro",
        "-e",
        "PYTHONPATH=/library",
        "-e",
        "HOME=/tmp",
        image,
        "/opt/venv/bin/python",
        "-c",
        code,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=20)
    if result.returncode:
        raise ValueError(result.stderr)
    data = json.loads(result.stdout.strip().splitlines()[-1])
    data["condition"] = arm
    rows.append(data)
    print(arm, sum(x["import_ok"] for x in data["modules"]), len(modules), flush=True)
(root / "diagnostics").mkdir(exist_ok=True)
(root / "diagnostics/import-check.json").write_text(json.dumps(rows, indent=2))
