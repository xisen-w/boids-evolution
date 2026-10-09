import copy
import json
import sys
from pathlib import Path

import pytest
from studies.tool_ecology.scripts import assemble_collection
from studies.tool_ecology.scripts.assemble_collection import validate_cell, validate_keys

from ecology.registry import Registry, file_hashes


def fixture():
    base = dict(
        protocol="v0.3.1-repeated-demand-entry-attribution",
        classification="exploratory",
        image="pinned",
        mini_swe_version="2.4.6",
        openai_version="pinned",
        reference_hashes={"ref.py": "reference"},
        source_hashes={"workload.py": "same", "model.py": "old"},
        parameters=dict(
            agents=8,
            rounds=6,
            steps=6,
            workers=4,
            seeds="71,108,2026",
            arms="local-neutral,local-boids,independent",
        ),
    )
    recovered = copy.deepcopy(base)
    recovered["source_hashes"]["model.py"] = "new"
    recovered["parameters"].update(seeds="108", arms="local-neutral")
    cfg = dict(agents=8, rounds=6, steps=6, workers=4, seed=108, condition="local-neutral")
    rows = [
        dict(author=f"a{i:02d}", round=r, publication_status="skip") for i in range(8) for r in range(1, 7)
    ]
    return base, recovered, cfg, rows, dict(physical_requests=288, errors=0)


def test_complete_zero_score_cell_is_valid_without_score_selection():
    base, m, cfg, rows, usage = fixture()
    assert validate_cell(base, m, cfg, rows, usage, m["source_hashes"]) == (108, "local-neutral")


@pytest.mark.parametrize(
    "fault", ["api_error", "incomplete", "duplicate", "wrong_protocol", "wrong_source", "wrong_seed"]
)
def test_recovery_rejects_invalid_or_incompatible_cells(fault):
    base, m, cfg, rows, usage = fixture()
    accepted = copy.deepcopy(m["source_hashes"])
    if fault == "api_error":
        usage["errors"] = 1
    elif fault == "incomplete":
        rows.pop()
    elif fault == "duplicate":
        rows[-1] = rows[0]
    elif fault == "wrong_protocol":
        m["protocol"] = "v0.3-repeated-demand"
    elif fault == "wrong_source":
        m["source_hashes"]["workload.py"] = "changed"
    elif fault == "wrong_seed":
        cfg["seed"] = 9001
    with pytest.raises(ValueError):
        validate_cell(base, m, cfg, rows, usage, accepted)


def test_collection_requires_all_nine_unique_planned_cells():
    keys = [(s, a) for s in (71, 108, 2026) for a in ("local-neutral", "local-boids", "independent")]
    validate_keys(keys)
    with pytest.raises(ValueError):
        validate_keys(keys[:-1])
    with pytest.raises(ValueError):
        validate_keys(keys + [keys[0]])


def test_assembly_copies_frozen_cells_preserves_aborted_base_and_all_costs(tmp_path, monkeypatch):
    base, recovered, _, rows, _ = fixture()
    ecology = Path(assemble_collection.__file__).resolve().parents[1] / "ecology"
    hashes = {k: v for k, v in file_hashes(ecology).items() if k.endswith(".py")}
    base.update(
        source_hashes=dict(hashes, **{"model.py": "old"}), code_revision="original", maximum_requests=2592
    )
    recovered.update(
        source_hashes=hashes,
        code_revision="recovery",
        maximum_requests=288,
        transport_policy=dict(timeout_seconds=180, max_retries=0),
    )

    def write(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def cell(run, seed, arm):
        root = run / f"seed-{seed}" / arm
        write(root / "config.json", dict(agents=8, rounds=6, steps=6, workers=4, seed=seed, condition=arm))
        records = copy.deepcopy(rows)
        records[0].update(publication_status="published", id="a00_r01")
        write(root / "records.json", records)
        write(root / "summary.json", dict(publications=1))
        write(
            root / "usage.json",
            dict(physical_requests=1, input_tokens=10, output_tokens=2, cached_tokens=0, errors=0),
        )
        write(root / "receipts.json", [])
        package = root / "registry/a00_r01"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("def empty(*args): return []\n")
        write(
            root / "registry/a00_r01.json",
            dict(id="a00_r01", author="a00", round=1, dependencies=[], hashes=file_hashes(package)),
        )
        registry = Registry(root / "registry")
        registry.freeze(root / "frozen")
        registry.materialize({"a00_r01"}, root / "builders/a00/round-01/judge-view")
        write(root / "builders/a00/round-01/service/result.json", dict(families={}))
        return root

    original = tmp_path / "demand-batch-02"
    write(original / "manifest.json", base)
    write(original / "ABORTED.json", dict(error_type="APITimeoutError"))
    valid_base = [(71, a) for a in ("local-neutral", "local-boids", "independent")] + [
        (108, a) for a in ("local-boids", "independent")
    ]
    for seed, arm in valid_base:
        cell(original, seed, arm)
    write(
        original / "seed-108/local-neutral/usage.json",
        dict(physical_requests=69, input_tokens=20, output_tokens=3, cached_tokens=0, errors=1),
    )
    output = tmp_path / "collection"
    monkeypatch.setattr(sys, "argv", ["assemble", str(original), "--output", str(output)])
    with pytest.raises(ValueError, match="missing completed recovery"):
        assemble_collection.main()
    assert not output.exists()
    for name, (seed, arm) in zip(
        assemble_collection.RECOVERIES,
        [(108, "local-neutral"), (2026, "independent"), (2026, "local-neutral"), (2026, "local-boids")],
        strict=True,
    ):
        run = tmp_path / name
        manifest = copy.deepcopy(recovered)
        manifest["parameters"].update(seeds=str(seed), arms=arm)
        write(run / "manifest.json", manifest)
        write(run / "COMPLETE.json", dict(societies=1))
        cell(run, seed, arm)
    before = file_hashes(original)
    assemble_collection.main()
    assembled = json.loads((output / "manifest.json").read_text())
    assert assembled["all_attempt_usage"]["physical_requests"] == 78
    assert assembled["included_cell_usage"]["physical_requests"] == 9
    assert assembled["discarded_attempt_usage"]["errors"] == 1
    assert assembled["code_revision"] is None
    assert assembled["code_revisions"] == ["original", "recovery"]
    assert "model.py" not in assembled["source_hashes"]
    assert len(assembled["lineage"]) == 9
    assert {entry["transport_policy"]["timeout_seconds"] for entry in assembled["lineage"]} == {55, 180}
    assert file_hashes(original) == before
    assert not (original / "COMPLETE.json").exists()
    for root in output.glob("seed-*/*"):
        Registry.verify_freeze(root / "frozen")
        assert (root / "builders/a00/round-01/service/result.json").exists()
        assert (root / "generation-manifest.json").exists()
