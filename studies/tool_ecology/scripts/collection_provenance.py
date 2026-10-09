"""Generation lineage and complete-attempt cost accounting for offline analyses."""

USAGE_KEYS = ("physical_requests", "input_tokens", "output_tokens", "cached_tokens", "errors")


def cell_provenance(manifest, cell):
    if "cell_manifests" in manifest and cell not in manifest["cell_manifests"]:
        raise ValueError("missing cell generation manifest")
    generation = manifest.get("cell_manifests", {}).get(cell, manifest)
    lineage = next((item for item in manifest.get("lineage", []) if item["cell"] == cell), {})
    policy = generation.get("transport_policy", lineage.get("transport_policy", {}))
    return dict(
        generation_code_revision=generation["code_revision"],
        timeout_seconds=policy.get("timeout_seconds"),
        max_retries=policy.get("max_retries"),
    )


def usage_accounting(manifest, rows):
    included = {key: sum(row[key] for row in rows) for key in USAGE_KEYS}
    if manifest.get("included_cell_usage", included) != included:
        raise ValueError("included-cell costs disagree with generation manifest")
    totals = manifest.get("all_attempt_usage", included)
    discarded = {key: totals[key] - included[key] for key in USAGE_KEYS}
    if any(value < 0 for value in discarded.values()):
        raise ValueError("attempt totals cannot omit included costs")
    if manifest.get("discarded_attempt_usage", discarded) != discarded:
        raise ValueError("discarded-attempt costs disagree with manifest")
    if totals["physical_requests"] > manifest["maximum_requests"]:
        raise ValueError("original request ceiling exceeded")
    return dict(
        all_attempt_usage=totals,
        included_cell_usage=included,
        discarded_attempt_usage=discarded,
        provider_money_cost=manifest.get("provider_money_cost", "unverified"),
        timeout_request_usage=manifest.get("timeout_request_usage", "not_applicable"),
    )
