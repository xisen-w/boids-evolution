import argparse
import json
import subprocess
from pathlib import Path

from .audit import audit
from .evaluate import evaluate, references
from .images import resolve_image
from .model import Budget
from .registry import Registry, file_hashes
from .study import build_society

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["audit", "references", "smoke"])
    parser.add_argument("--tasks", type=Path, default=ROOT / "external/ldb-tasks")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image", default="boids-pyda:20261008")
    parser.add_argument("--key-file", type=Path, default=Path("/tmp/boids-agentport.key"))
    parser.add_argument("--agents", type=int, default=4)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--builder-steps", type=int, default=6)
    parser.add_argument("--consumer-steps", type=int, default=12)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("output already exists; no silent resume or overwrite")
    args.output.mkdir(parents=True)
    audit(args.tasks, args.output / "task-audit.json")
    if args.mode == "audit":
        return
    image = resolve_image(args.image)
    if args.mode == "references":
        references(args.tasks, args.output / "references", image)
        return
    revision = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain"], text=True)
    if dirty:
        raise RuntimeError("commit code before paid run")
    manifest = dict(
        code_revision=revision,
        image=image,
        protocol="v0.2-dependency-bundles",
        parameters={
            k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items() if k != "key_file"
        },
        source_hashes=file_hashes(ROOT / "ecology"),
        classification="engineering_pre_freeze",
        request_limit=240,
        output_token_reservation_limit=700000,
        provider_money_cost="unverified",
    )
    import importlib.metadata

    import minisweagent

    manifest["installed_runtime"] = {
        "mini_swe_agent_version": importlib.metadata.version("mini-swe-agent"),
        "openai_version": importlib.metadata.version("openai"),
        "mini_swe_agent_hashes": file_hashes(Path(minisweagent.__file__).parent),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    key = args.key_file.read_text().strip()
    budget = Budget(args.output / "api", call_limit=240, output_limit=700000)
    summary = {}
    # Build both societies BEFORE revealing any held-out results to the developer.
    libraries = {}
    for condition in ["local-neutral", "local-boids"]:
        root = args.output / condition
        root.mkdir()
        libraries[condition] = build_society(
            root,
            args.tasks,
            image,
            budget,
            key,
            condition,
            n=args.agents,
            rounds=args.rounds,
            steps=args.builder_steps,
        )
    empty = args.output / "no-library"
    empty.mkdir()
    libraries["no-library"] = Registry(empty / "registry").freeze(empty / "frozen")
    for condition, frozen in libraries.items():
        evalroot = args.output / condition / "evaluation"
        evalroot.mkdir()
        summary[condition] = evaluate(
            evalroot, args.tasks, frozen, image, budget, key, steps=args.consumer_steps
        )
        (args.output / "summary.json").write_text(json.dumps(summary, indent=2))
    usage = {
        "physical_requests": budget.calls,
        "input_tokens": 0,
        "output_tokens": 0,
        "cached_tokens": 0,
        "errors": 0,
    }
    for p in (args.output / "api").glob("response-*.json"):
        r = json.loads(p.read_text())
        usage["errors"] += int("error_type" in r)
        u = r.get("usage") or {}
        for k in ("input_tokens", "output_tokens"):
            usage[k] += u.get(k, 0)
        usage["cached_tokens"] += (u.get("input_tokens_details") or {}).get("cached_tokens", 0)
    (args.output / "usage.json").write_text(json.dumps(usage, indent=2))
    print(json.dumps(usage), flush=True)


if __name__ == "__main__":
    main()
