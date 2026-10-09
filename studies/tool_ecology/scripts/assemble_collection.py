"""Copy nine explicitly recovered cells into a separate analysis collection.

Never resumes or modifies the aborted base, and never selects by semantic score.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from ecology.registry import Registry, file_hashes

PROTOCOL = "v0.3.1-repeated-demand-entry-attribution"
ARMS = ("local-neutral", "local-boids", "independent")
SEEDS = (71, 108, 2026)
RECOVERIES = (
    "demand-recovery-108-neutral-01",
    "demand-recovery-2026-independent-01",
    "demand-recovery-2026-neutral-01",
    "demand-recovery-2026-boids-01",
)
USAGE_KEYS = ("physical_requests", "input_tokens", "output_tokens", "cached_tokens", "errors")


def validate_cell(base, manifest, cfg, rows, usage, recovery_hashes):
    for key in (
        "protocol",
        "classification",
        "image",
        "mini_swe_version",
        "openai_version",
        "reference_hashes",
    ):
        if manifest[key] != base[key]:
            raise ValueError(f"incompatible {key}")
    if manifest["protocol"] != PROTOCOL or manifest["classification"] != "exploratory":
        raise ValueError("wrong scientific protocol")
    if manifest["source_hashes"] not in (base["source_hashes"], recovery_hashes):
        raise ValueError("unexpected runtime source")
    for key, expected in dict(agents=8, rounds=6, steps=6, workers=4).items():
        if cfg[key] != expected or manifest["parameters"][key] != expected:
            raise ValueError(f"wrong {key}")
    identity = cfg["seed"], cfg["condition"]
    if identity[0] not in SEEDS or identity[1] not in ARMS:
        raise ValueError("unplanned cell")
    if str(identity[0]) not in manifest["parameters"]["seeds"].split(",") or identity[1] not in manifest[
        "parameters"
    ]["arms"].split(","):
        raise ValueError("cell not in source manifest")
    expected_rows = {(f"a{i:02d}", r) for i in range(8) for r in range(1, 7)}
    if len(rows) != 48 or {(r["author"], r["round"]) for r in rows} != expected_rows:
        raise ValueError("incomplete or duplicated opportunities")
    if usage["errors"] or not 0 < usage["physical_requests"] <= 288:
        raise ValueError("API failure or request limit")
    return identity


def validate_keys(keys):
    if len(keys) != 9 or set(keys) != {(s, a) for s in SEEDS for a in ARMS}:
        raise ValueError("need all nine unique planned cells")


def read(path):
    return json.loads(path.read_text())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("base", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise ValueError("preserve existing collection")
    if (
        read(args.base / "ABORTED.json")["error_type"] != "APITimeoutError"
        or (args.base / "INVALIDATED_MEASUREMENT.json").exists()
    ):
        raise ValueError("only corrected transport-aborted base is eligible")
    base = read(args.base / "manifest.json")
    ecology = Path(__file__).resolve().parents[1] / "ecology"
    recovery_hashes = {k: v for k, v in file_hashes(ecology).items() if k.endswith(".py")}
    changed = {
        k
        for k in base["source_hashes"].keys() | recovery_hashes.keys()
        if base["source_hashes"].get(k) != recovery_hashes.get(k)
    }
    if changed - {"model.py", "dynamics.py"}:
        raise ValueError("recovery may only change transport and manifest metadata")
    run_roots = [args.base]
    for name in RECOVERIES:
        root = args.base.parent / name
        if not (root / "COMPLETE.json").exists() or read(root / "COMPLETE.json")["societies"] != 1:
            raise ValueError(f"missing completed recovery: {name}")
        run_roots.append(root)
    cells, inventory = [], []
    for run in run_roots:
        manifest = read(run / "manifest.json")
        for root in sorted(run.glob("seed-*/*")):
            if not (root / "usage.json").exists():
                continue
            usage = read(root / "usage.json")
            inventory.append(
                dict(
                    source_society=str(root.resolve()), frozen=(root / "frozen/freeze.json").exists(), **usage
                )
            )
            if not (root / "frozen/freeze.json").exists():
                continue
            Registry.verify_freeze(root / "frozen")
            cfg, rows = read(root / "config.json"), read(root / "records.json")
            key = validate_cell(base, manifest, cfg, rows, usage, recovery_hashes)
            cells.append((key, root, manifest, cfg, rows, usage))
    validate_keys([c[0] for c in cells])
    totals = {k: sum(row[k] for row in inventory) for k in USAGE_KEYS}
    included = {k: sum(c[5][k] for c in cells) for k in USAGE_KEYS}
    if totals["physical_requests"] > base["maximum_requests"]:
        raise ValueError("original total request ceiling exceeded")
    args.output.mkdir(parents=True)
    manifests, lineage, summaries = {}, [], []
    for (seed, arm), root, manifest, cfg, rows, usage in sorted(cells):
        key = f"seed-{seed}/{arm}"
        dest = args.output / key
        dest.mkdir(parents=True)
        for name in ("config.json", "records.json", "summary.json", "usage.json", "receipts.json"):
            shutil.copyfile(root / name, dest / name)
        for name in ("registry", "frozen"):
            shutil.copytree(root / name, dest / name)
        for row in rows:
            if row["publication_status"] != "published":
                continue
            slot = Path("builders") / row["author"] / f"round-{row['round']:02d}"
            for name in ("judge-view", "service"):
                shutil.copytree(root / slot / name, dest / slot / name)
        (dest / "generation-manifest.json").write_text(json.dumps(manifest, indent=2))
        manifests[key] = manifest
        lineage.append(
            dict(
                cell=key,
                source_society=str(root.resolve()),
                code_revision=manifest["code_revision"],
                transport_policy=manifest.get(
                    "transport_policy",
                    dict(timeout_seconds=55, max_retries=0, provenance="original_pinned_model_source"),
                ),
                source_manifest_sha256=hashlib.sha256(
                    (root.parents[1] / "manifest.json").read_bytes()
                ).hexdigest(),
                freeze_manifest_sha256=hashlib.sha256((root / "frozen/freeze.json").read_bytes()).hexdigest(),
            )
        )
        summaries.append(dict(seed=seed, condition=arm, **read(root / "summary.json")))
    common = {
        k: v
        for k, v in base["source_hashes"].items()
        if all(m["source_hashes"].get(k) == v for m in manifests.values())
    }
    collection = dict(
        protocol=PROTOCOL,
        classification="exploratory_recovered_collection",
        code_revision=None,
        code_revisions=sorted({m["code_revision"] for m in manifests.values()}),
        image=base["image"],
        parameters=dict(base["parameters"], output=str(args.output)),
        source_hashes=common,
        source_hash_policy="shared identical files only; full hashes and revisions in cell_manifests",
        reference_hashes=base["reference_hashes"],
        cell_manifests=manifests,
        lineage=lineage,
        all_attempt_usage=totals,
        included_cell_usage=included,
        discarded_attempt_usage={k: totals[k] - included[k] for k in USAGE_KEYS},
        attempt_inventory=inventory,
        original_batch_status="aborted_APITimeoutError",
        maximum_requests=base["maximum_requests"],
        provider_money_cost="unverified",
        timeout_request_usage="unknown_not_free",
        assembly_code_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        assembly_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    for name, value in (
        ("manifest.json", collection),
        ("summary.json", summaries),
        ("COLLECTION.json", dict(lineage=lineage, all_attempt_usage=totals, attempt_inventory=inventory)),
        (
            "COMPLETE.json",
            dict(societies=9, status="complete_recovered_exploratory_collection", uninterrupted_batch=False),
        ),
    ):
        (args.output / name).write_text(json.dumps(value, indent=2))
    print(json.dumps(dict(societies=9, **totals)), flush=True)


if __name__ == "__main__":
    main()
