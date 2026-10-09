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
library = root / "local-boids/frozen"
instrument = Path.cwd() / "ecology/instrument"
expected = [
    {"team": "A", "sum": 5.0, "mean": 2.5, "count": 2},
    {"team": "B", "sum": 7.0, "mean": 7.0, "count": 1},
]
code = r"""import json,pyarrow as pa,pyarrow.parquet as pq
from pathlib import Path
from published.a03_r03 import summarize
Path('/workspace/probe.csv').write_text('team,value\nA,2\nA,3\nB,7\n')
pq.write_table(pa.Table.from_pylist([{'team':'A','value':2},{'team':'A','value':3},{'team':'B','value':7}]),'/workspace/probe.parquet')
result={}
for fmt in ['csv','parquet']:
 try:result[fmt]={'output':summarize('/workspace/probe.'+fmt,'team',{'sum':('value','sum'),'mean':('value','mean'),'count':('value','count')},schema={'value':float})}
 except Exception as exc:result[fmt]={'error_type':type(exc).__name__,'error':str(exc)}
print(json.dumps(result))
"""
rows = []
for label, edge in [
    ("baseline", ""),
    ("upstream_conversion_intervention", "published.a00_r01->published.a00_r01._convert"),
]:
    out = root / "diagnostics/real-tool-witness" / label
    workspace = out / "workspace"
    traces = out / "traces"
    workspace.mkdir(parents=True)
    traces.mkdir()
    name = "boids-witness-" + uuid.uuid4().hex[:12]
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
        str(workspace) + ":/workspace:rw",
        "-v",
        str(library) + ":/library:ro",
        "-v",
        str(instrument) + ":/instrument:ro",
        "-v",
        str(traces) + ":/trace:rw",
        "-e",
        "PYTHONPATH=/library:/instrument",
        "-e",
        "BOIDS_ABLATE_EDGE=" + edge,
        image,
        "/opt/venv/bin/python",
        "-c",
        code,
    ]
    (out / "command.json").write_text(json.dumps(command, indent=2))
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=20)
    (out / "stdout.txt").write_text(result.stdout)
    (out / "stderr.txt").write_text(result.stderr)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout.strip().splitlines()[-1])
    edges = {}
    for path in traces.glob("*.json"):
        for k, v in json.loads(path.read_text()).items():
            row = edges.setdefault(k, dict(calls=0, mutated=0, exceptions=0))
            for key in row:
                row[key] += v.get(key, 0)
    rows.append(dict(case=label, outputs=data, edges=edges, process_returncode=result.returncode))
    print(label, data, flush=True)
assert rows[0]["outputs"]["csv"]["output"] == expected
cross = "published.a03_r03->published.a00_r01.iter_rows"
assert rows[0]["edges"][cross]["calls"] > 0
assert rows[1]["edges"]["published.a00_r01->published.a00_r01._convert"]["mutated"] > 0
assert rows[1]["outputs"]["csv"]["output"] != expected
summary = dict(
    classification="host_authored_posthoc_engineering_probe_not_a_scored_consumer_or_emergence_claim",
    cross_author_csv_composition=True,
    noncrashing_upstream_intervention_changed_output=True,
    parquet_baseline=rows[0]["outputs"]["parquet"],
    rows=rows,
)
(root / "diagnostics/real-tool-witness/results.json").write_text(json.dumps(summary, indent=2))
