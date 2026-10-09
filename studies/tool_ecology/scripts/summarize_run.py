import argparse
import ast
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("run", type=Path)
args = parser.parse_args()
root = args.run.resolve()
manifest = json.loads((root / "manifest.json").read_text())
requests = {p.stem.split("-")[1]: json.loads(p.read_text()) for p in (root / "api").glob("request-*.json")}
usage_by_label = defaultdict(
    lambda: dict(requests=0, input_tokens=0, output_tokens=0, cached_tokens=0, errors=0)
)
for index, request in requests.items():
    row = usage_by_label[request["label"]]
    row["requests"] += 1
    response = root / "api" / f"response-{index}.json"
    if not response.exists():
        raise ValueError(f"missing response {index}")
    raw = json.loads(response.read_text())
    row["errors"] += int("error_type" in raw)
    u = raw.get("usage") or {}
    for k in ["input_tokens", "output_tokens"]:
        row[k] += u.get(k, 0)
    row["cached_tokens"] += (u.get("input_tokens_details") or {}).get("cached_tokens", 0)

summary = dict(
    run=root.name, code_revision=manifest["code_revision"], usage_by_label=dict(usage_by_label), conditions={}
)
for condition in ["local-neutral", "local-boids", "no-library"]:
    arm = root / condition
    cards = {p.stem: json.loads(p.read_text()) for p in (arm / "registry").glob("*.json")}
    builders = json.loads((arm / "builders.json").read_text()) if (arm / "builders.json").exists() else []
    receipts = json.loads((arm / "receipts.json").read_text()) if (arm / "receipts.json").exists() else []
    violations = []
    for b in builders:
        own = {i for i, c in cards.items() if c["author"] == b["author"] and c["round"] < b["round"]}
        received = {
            r["member"]
            for r in receipts
            if r["recipient"] == b["author"] and r["available_round"] <= b["round"]
        }
        if own | received != set(b["visible"]):
            violations.append([b["author"], b["round"]])
    edges = [dict(source=c["id"], target=d) for c in cards.values() for d in c["dependencies"]]
    cross = [e for e in edges if e["source"].split("_")[0] != e["target"].split("_")[0]]
    frozen = arm / "frozen"
    expected = json.loads((frozen / "freeze.json").read_text())["hashes"]
    actual = {
        str(p.relative_to(frozen)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in frozen.rglob("*")
        if p.is_file() and p != frozen / "freeze.json"
    }
    if expected != actual:
        raise ValueError("freeze mismatch")
    escaping = []
    for package in (arm / "registry").iterdir():
        if not package.is_dir():
            continue
        for file in package.rglob("*.py"):
            for node in ast.walk(ast.parse(file.read_text())):
                if isinstance(node, ast.ImportFrom) and node.level > len(file.relative_to(package).parts):
                    escaping.append(str(file))
    grades = []
    for result in sorted((arm / "evaluation").glob("*/grade/result.json")):
        data = json.loads(result.read_text())
        slot = result.parents[1]
        submitted = slot / "submitted"
        imports = []
        for py in submitted.rglob("*.py"):
            for line in py.read_text().splitlines():
                if "published" in line:
                    imports.append(line.strip())
        trajectory = json.loads((slot / "trajectory.json").read_text())["info"]
        direct = {
            k: v
            for k, v in data["executed_python_edges"].items()
            if not k.split("->")[0].startswith("published.")
        }
        crossed = {
            k: v
            for k, v in data["executed_python_edges"].items()
            if k.startswith("published.")
            and k.split("->")[0].split(".")[1].split("_")[0] != k.split("->")[1].split(".")[1].split("_")[0]
        }
        grades.append(
            dict(
                problem=slot.name,
                passed=data["passed"],
                total=data["total"],
                strict_success=data["strict_success"],
                ldb_score=data["ldb_score"],
                consumer_calls=trajectory["model_stats"]["api_calls"],
                consumer_exit=trajectory["exit_status"],
                direct_tool_calls=direct,
                cross_author_executed_calls=crossed,
                submitted_published_mentions=imports,
            )
        )
    labels = {k: v for k, v in usage_by_label.items() if k.startswith(condition + "/")}
    builder_usage = {
        k: sum(v[k] for v in labels.values())
        for k in ["requests", "input_tokens", "output_tokens", "cached_tokens", "errors"]
    }
    summary["conditions"][condition] = dict(
        publications=len(cards),
        publication_statuses=dict(Counter(b["publication_status"] for b in builders)),
        builder_exit_statuses=dict(Counter(b["execution"]["exit_status"] for b in builders)),
        declared_dependencies=edges,
        declared_cross_author_dependencies=cross,
        receipt_entries=len(receipts),
        snapshot_violations=violations,
        frozen_hashes_verified=True,
        escaping_relative_imports=escaping,
        builder_usage=builder_usage,
        grades=grades,
    )

symlinks = [str(p.relative_to(root)) for p in root.rglob("*") if p.is_symlink()]
summary["symlinks"] = symlinks
repo = Path(__file__).resolve().parent if (Path(__file__).resolve().parent / ".git").exists() else Path.cwd()
checked = []
for name, expected in manifest["source_hashes"].items():
    if not name.endswith(".py"):
        continue
    content = subprocess.check_output(
        ["git", "show", f"{manifest['code_revision']}:ecology/{name}"], cwd=repo
    )
    if hashlib.sha256(content).hexdigest() != expected:
        raise ValueError(f"source mismatch {name}")
    checked.append(name)
summary["manifest_source_files_verified_against_commit"] = checked
summary["usage"] = json.loads((root / "usage.json").read_text())
if summary["usage"]["physical_requests"] != len(requests):
    raise ValueError("request count mismatch")
(root / "analysis.json").write_text(json.dumps(summary, indent=2))
print(
    json.dumps(
        {k: v for k, v in summary.items() if k in ["run", "code_revision", "usage", "symlinks"]}, indent=2
    )
)
