"""Read-only host audit of generation Git blobs and archived API metadata.

Publishes only counts/settings/hashes, never request inputs or response contents.
Requires the private original run directories referenced by the collection.
"""

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from ecology.registry import Registry, file_hashes

CORE = Path(__file__).resolve().parents[3]
USAGE_KEYS = ("physical_requests", "input_tokens", "output_tokens", "cached_tokens", "errors")


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("collection", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("preserve earlier provenance audit")
    if not (args.collection / "COMPLETE.json").exists():
        raise ValueError("collection must be complete")
    manifest = read(args.collection / "manifest.json")
    blob_cache = {}
    for lineage in manifest["lineage"]:
        root = Path(lineage["source_society"])
        source = root.parents[1] / "manifest.json"
        generation = read(source)
        if hashlib.sha256(source.read_bytes()).hexdigest() != lineage["source_manifest_sha256"]:
            raise ValueError("source manifest changed")
        for key, prefix in (
            ("source_hashes", "studies/tool_ecology/ecology"),
            ("reference_hashes", "boidsnet/env"),
        ):
            for name, expected in generation[key].items():
                spec = f"{generation['code_revision']}:{prefix}/{name}"
                if spec not in blob_cache:
                    data = subprocess.check_output(["git", "-C", str(CORE), "show", spec])
                    blob_cache[spec] = hashlib.sha256(data).hexdigest()
                if blob_cache[spec] != expected:
                    raise ValueError(f"generation Git blob differs: {spec}")
        Registry.verify_freeze(root / "frozen")
        Registry.verify_freeze(args.collection / lineage["cell"] / "frozen")
        if (
            hashlib.sha256((root / "frozen/freeze.json").read_bytes()).hexdigest()
            != lineage["freeze_manifest_sha256"]
        ):
            raise ValueError("source freeze manifest changed")
    for name, expected in manifest["source_hashes"].items():
        if (
            hashlib.sha256((CORE / "studies/tool_ecology/ecology" / name).read_bytes()).hexdigest()
            != expected
        ):
            raise ValueError(f"shared current analysis runtime differs: {name}")
    reference = {k: v for k, v in file_hashes(CORE / "boidsnet/env").items() if k.endswith(".py")}
    if reference != manifest["reference_hashes"]:
        raise ValueError("current reference source differs")
    attempts = []
    for item in manifest["attempt_inventory"]:
        root = Path(item["source_society"])
        requests = sorted((root / "api").glob("request-*.json"))
        responses = sorted((root / "api").glob("response-*.json"))
        if len(requests) != item["physical_requests"] or len(responses) != len(requests):
            raise ValueError("archived request/response count mismatch")
        usage = dict.fromkeys(USAGE_KEYS, 0)
        usage["physical_requests"] = len(requests)
        models, errors = Counter(), Counter()
        for request in requests:
            payload = read(request)["payload"]
            if (
                payload["model"] != "azure:gpt-6-luna"
                or payload["reasoning"] != {"effort": "low"}
                or payload["max_output_tokens"] != 3000
                or payload["parallel_tool_calls"]
            ):
                raise ValueError("unexpected API model/settings")
            response = read(request.with_name(request.name.replace("request-", "response-")))
            if "error_type" in response:
                errors[response["error_type"]] += 1
                usage["errors"] += 1
            else:
                if response["model"] != "gpt-6-luna":
                    raise ValueError("unexpected provider model")
                models[response["model"]] += 1
            tokens = response.get("usage") or {}
            for key in ("input_tokens", "output_tokens"):
                usage[key] += tokens.get(key, 0)
            usage["cached_tokens"] += (tokens.get("input_tokens_details") or {}).get("cached_tokens", 0)
        if any(usage[key] != item[key] for key in USAGE_KEYS):
            raise ValueError("API metadata and archived usage disagree")
        attempts.append(
            dict(
                source_run=root.parents[1].name,
                cell=f"{root.parent.name}/{root.name}",
                included_frozen_cell=item["frozen"],
                returned_models=dict(models),
                error_types=dict(errors),
                **usage,
            )
        )
    total = {key: sum(row[key] for row in attempts) for key in USAGE_KEYS}
    if total != manifest["all_attempt_usage"]:
        raise ValueError("collection totals disagree with original API metadata")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            dict(
                classification="read_only_generation_and_API_metadata_audit",
                generation_Git_blobs_verified=len(blob_cache),
                included_frozen_cells_verified=len(manifest["lineage"]),
                requested_model="azure:gpt-6-luna",
                returned_model="gpt-6-luna",
                reasoning_effort="low",
                max_output_tokens=3000,
                model_calls_for_audit=0,
                all_attempt_usage=total,
                attempts=attempts,
                timeout_provider_usage="unknown_not_free",
                analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            ),
            indent=2,
        )
    )
    print(
        json.dumps(dict(generation_blobs=len(blob_cache), cells=len(manifest["lineage"]), **total)),
        flush=True,
    )


if __name__ == "__main__":
    main()
