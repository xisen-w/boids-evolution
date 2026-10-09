import argparse
import difflib
import hashlib
import json
import shutil
from pathlib import Path

from ecology.evaluate import grade
from ecology.registry import Registry

p = argparse.ArgumentParser()
p.add_argument("run", type=Path)
args = p.parse_args()
root = args.run.resolve()
manifest = json.loads((root / "manifest.json").read_text())
tasks = Path(manifest["parameters"]["tasks"])
problem = tasks / "pyda/evaluation/weather-features"
slot = root / "local-boids/evaluation/weather-features"
out = root / "diagnostics/boids-weather-extension"
workspace = out / "workspace"
out.mkdir(parents=True)
shutil.copytree(problem / "workspace", workspace)
for source in (slot / "submitted").rglob("*.py"):
    target = workspace / source.relative_to(slot / "submitted")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
source = workspace / "main.py"
before = source.read_text()
old = "{'csv':'csv','jsonl':'jsonl','ndjson':'jsonl','parquet':'parquet','pq':'parquet'}"
new = "{'.csv':'csv','.jsonl':'jsonl','.ndjson':'jsonl','.parquet':'parquet','.pq':'parquet'}"
assert before.count(old) == 1
after = before.replace(old, new)
source.write_text(after)
(out / "main.diff").write_text(
    "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile="frozen-submission",
            tofile="posthoc-diagnostic-only",
        )
    )
)
(out / "amendment.json").write_text(
    json.dumps(
        dict(
            classification="posthoc_diagnosis_excluded_from_primary",
            model_calls=0,
            change="include leading dot in extension lookup keys",
            before_sha256=hashlib.sha256(before.encode()).hexdigest(),
            after_sha256=hashlib.sha256(after.encode()).hexdigest(),
        ),
        indent=2,
    )
)
library = root / "local-boids/frozen"
Registry.verify_freeze(library)
result = grade(workspace, library, problem, out / "grade", manifest["image"])
Registry.verify_freeze(library)
print(json.dumps({k: result[k] for k in ["passed", "total", "strict_success", "ldb_score"]}), flush=True)
