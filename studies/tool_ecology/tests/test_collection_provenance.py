import pytest
from studies.tool_ecology.scripts.collection_provenance import cell_provenance, usage_accounting


def usage(calls, errors=0):
    return dict(physical_requests=calls, input_tokens=100, output_tokens=10, cached_tokens=50, errors=errors)


def test_aborted_attempt_cost_and_unknown_timeout_are_not_dropped():
    included, total = usage(200), usage(269, errors=1)
    total.update(input_tokens=120, output_tokens=12, cached_tokens=60)
    manifest = dict(
        maximum_requests=2592,
        all_attempt_usage=total,
        included_cell_usage=included,
        timeout_request_usage="unknown_not_free",
    )
    accounting = usage_accounting(manifest, [included])
    assert accounting["all_attempt_usage"]["physical_requests"] == 269
    assert accounting["discarded_attempt_usage"]["physical_requests"] == 69
    assert accounting["discarded_attempt_usage"]["errors"] == 1
    assert accounting["timeout_request_usage"] == "unknown_not_free"
    with pytest.raises(ValueError):
        usage_accounting(dict(manifest, included_cell_usage=usage(199)), [included])
    with pytest.raises(ValueError):
        usage_accounting(dict(manifest, all_attempt_usage=usage(199)), [included])


def test_uniform_run_still_uses_included_costs():
    row = usage(200)
    assert usage_accounting(dict(maximum_requests=288), [row])["all_attempt_usage"] == row


def test_per_cell_revision_and_transport_are_preserved():
    old = dict(code_revision="original")
    new = dict(code_revision="recovery", transport_policy=dict(timeout_seconds=180, max_retries=0))
    manifest = dict(
        code_revision=None,
        cell_manifests={"seed-71/local-neutral": old, "seed-108/local-neutral": new},
        lineage=[
            dict(cell="seed-71/local-neutral", transport_policy=dict(timeout_seconds=55, max_retries=0))
        ],
    )
    assert cell_provenance(manifest, "seed-71/local-neutral") == dict(
        generation_code_revision="original",
        timeout_seconds=55,
        max_retries=0,
    )
    assert cell_provenance(manifest, "seed-108/local-neutral") == dict(
        generation_code_revision="recovery",
        timeout_seconds=180,
        max_retries=0,
    )
    assert cell_provenance(new, "seed-108/local-neutral")["generation_code_revision"] == "recovery"
    with pytest.raises(ValueError, match="missing cell"):
        cell_provenance(manifest, "seed-2026/local-neutral")
