import json

from minisweagent.models.test_models import DeterministicModel, make_output

from ecology import dynamics
from ecology.images import resolve_image


def test_real_round_snapshot_barrier_with_offline_inference(tmp_path, monkeypatch):
    command = """python - <<'PY'
from pathlib import Path
import json
p=Path('candidate'); p.mkdir()
(p/'__init__.py').write_text('def serve(rows, lookup, request): return []\\n')
(p/'README.md').write_text('Intentionally incomplete fixture')
(p/'publish.json').write_text(json.dumps(dict(description='fixture',checks={'clean':'serve'},dependencies=[])))
PY"""

    def model(*args, **kwargs):
        return DeterministicModel(
            outputs=[
                make_output("", [{"command": x}], 0)
                for x in [command, "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"]
            ]
        )

    monkeypatch.setattr(dynamics, "AgentPortModel", model)
    root = tmp_path / "society"
    got = dynamics.run_society(
        root,
        "local-neutral",
        resolve_image("boids-pyda:20261008"),
        "host-fixture",
        seed=71,
        n=3,
        rounds=2,
        steps=3,
        workers=3,
    )
    rows = json.loads((root / "records.json").read_text())
    assert len(rows) == 6
    assert all(r["visible"] == [] for r in rows if r["round"] == 1)
    assert all(
        len(r["visible"]) == 3 and all(x.endswith("_r01") for x in r["visible"])
        for r in rows
        if r["round"] == 2
    )
    assert got["verified_family_coverage"] == []
    assert got["correct_publications"] == 0
    assert got["publications"] == 6
    for slot in (root / "builders").glob("*/round-01"):
        assert json.loads((slot / "view/catalogue.json").read_text()) == []


def test_partial_correct_reuse_is_recorded_without_verified_family():
    edge = "published.a01_r02->published.a00_r01.clean"
    result = dict(
        families={"clean": {"passed": 5, "total": 6}},
        details=[dict(family="clean", correct=i < 5, executed_edges=[edge]) for i in range(6)],
    )
    got = dynamics.service_evidence(result)
    assert got["verified_families"] == []
    assert got["cross_author_edges"] == [edge]
    assert got["verified_cross_author_edges"] == []
    assert got["correct_cross_author_requests"] == 5
    assert got["correct_service_requests"] == 5
