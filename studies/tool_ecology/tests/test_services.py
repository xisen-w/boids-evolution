import json

from ecology.images import resolve_image
from ecology.registry import Registry
from ecology.services import judge


def packet(root, name, code, checks, deps=()):
    path = root / name
    path.mkdir()
    (path / "__init__.py").write_text(code)
    (path / "README.md").write_text("Fixture API documentation")
    (path / "publish.json").write_text(
        json.dumps(dict(description=name, checks=checks, dependencies=list(deps)))
    )
    return path


def test_real_service_correct_cross_author_and_noncrashing_intervention(tmp_path):
    reg = Registry(tmp_path / "registry")
    code = """def clean(rows, lookup, request):
    out = [dict(r) for r in rows]
    vals = sorted(r['units'] for r in rows if r.get('units') is not None)
    fill = 0 if not vals or request['fill']=='zero' else sum(vals)/len(vals) if request['fill']=='mean' else vals[len(vals)//2] if len(vals)%2 else (vals[len(vals)//2-1]+vals[len(vals)//2])/2
    for r in out:
        if isinstance(r.get('region'), str): r['region']=r['region'].strip().lower()
        if r.get('units') is None: r['units']=fill
    return out
"""
    first = reg.publish("a00", 1, packet(tmp_path, "one", code, {"clean": "clean"}), allowed=set())
    second = reg.publish(
        "a01",
        2,
        packet(
            tmp_path,
            "two",
            f"from published.{first} import clean\ndef serve(rows, lookup, request):\n    return clean(rows, lookup, request)\n",
            {"clean": "serve"},
            [first],
        ),
        allowed={first},
    )
    frozen = reg.freeze(tmp_path / "frozen")
    image = resolve_image("boids-pyda:20261008")
    baseline = judge(frozen, reg.artifacts[second], tmp_path / "baseline", image, seed=71, round_=2)
    assert baseline["families"]["clean"]["passed"] == 6
    edge = f"published.{second}->published.{first}.clean"
    assert baseline["edges"][edge]["calls"] == 6
    mutation = judge(
        frozen, reg.artifacts[second], tmp_path / "mutated", image, seed=71, round_=2, ablate_edge=edge
    )
    assert mutation["families"]["clean"]["passed"] < 6
    assert mutation["families"]["clean"]["crashed"] == 0
    assert mutation["edges"][edge]["mutated"] > 0
    plain = judge(
        frozen, reg.artifacts[second], tmp_path / "plain", image, seed=71, round_=2, instrument=False
    )
    assert plain["families"] == baseline["families"]
    assert plain["edges"] == {}


def test_mutation_of_inputs_is_not_valid_service(tmp_path):
    reg = Registry(tmp_path / "registry")
    tool = reg.publish(
        "a00",
        1,
        packet(
            tmp_path,
            "one",
            "def f(rows, lookup, request):\n    rows.clear()\n    return []\n",
            {"clean": "f"},
        ),
        allowed=set(),
    )
    frozen = reg.freeze(tmp_path / "frozen")
    got = judge(
        frozen,
        reg.artifacts[tool],
        tmp_path / "judge",
        resolve_image("boids-pyda:20261008"),
        seed=71,
        round_=1,
    )
    assert got["families"]["clean"]["passed"] == 1  # originally empty case only
    assert got["families"]["clean"]["input_mutations"] == 5


def test_docker_start_failure_is_infrastructure_error(tmp_path):
    import pytest

    reg = Registry(tmp_path / "registry")
    tool = reg.publish(
        "a00",
        1,
        packet(tmp_path, "one", "def f(rows, lookup, request): return []\n", {"clean": "f"}),
        allowed=set(),
    )
    frozen = reg.freeze(tmp_path / "frozen")
    with pytest.raises(RuntimeError, match="infrastructure"):
        judge(frozen, reg.artifacts[tool], tmp_path / "judge", "INVALID_IMAGE_NAME", seed=71, round_=1)


def test_one_non_json_output_does_not_erase_other_case_evidence(tmp_path):
    reg = Registry(tmp_path / "registry")
    code = (
        'def bad(rows, lookup, request): return float("nan")\ndef empty(rows, lookup, request): return []\n'
    )
    tool = reg.publish(
        "a00", 1, packet(tmp_path, "one", code, {"clean": "bad", "revenue": "empty"}), allowed=set()
    )
    frozen = reg.freeze(tmp_path / "frozen")
    got = judge(
        frozen,
        reg.artifacts[tool],
        tmp_path / "judge",
        resolve_image("boids-pyda:20261008"),
        seed=71,
        round_=1,
    )
    assert got["families"]["revenue"]["passed"] == 1
    assert got["families"]["clean"]["crashed"] == 6


def test_oversized_generated_outputs_are_capability_failure_not_batch_abort(tmp_path):
    reg = Registry(tmp_path / "registry")
    code = 'def bad(rows, lookup, request): return "x"*400000\n'
    tool = reg.publish("a00", 1, packet(tmp_path, "one", code, {"clean": "bad"}), allowed=set())
    frozen = reg.freeze(tmp_path / "frozen")
    got = judge(
        frozen,
        reg.artifacts[tool],
        tmp_path / "judge",
        resolve_image("boids-pyda:20261008"),
        seed=71,
        round_=1,
    )
    assert got["families"]["clean"]["passed"] == 0
    assert got["families"]["clean"]["crashed"] == 6


def test_native_instance_method_reuse_is_traced_and_intervened(tmp_path):
    reg = Registry(tmp_path / "registry")
    code = """import statistics
class Cleaner:
    def clean(self, rows, lookup, request):
        values=[r['units'] for r in rows if r.get('units') is not None]
        fill=0 if not values or request['fill']=='zero' else statistics.mean(values) if request['fill']=='mean' else statistics.median(values)
        out=[dict(r) for r in rows]
        for r in out:
            if isinstance(r.get('region'),str): r['region']=r['region'].strip().lower()
            if r.get('units') is None: r['units']=fill
        return out
"""
    first = reg.publish("a00", 1, packet(tmp_path, "one", code, {}), allowed=set())
    second = reg.publish(
        "a01",
        2,
        packet(
            tmp_path,
            "two",
            f"from published.{first} import Cleaner\ndef serve(rows, lookup, request): return Cleaner().clean(rows,lookup,request)\n",
            {"clean": "serve"},
            [first],
        ),
        allowed={first},
    )
    frozen = reg.freeze(tmp_path / "frozen")
    image = resolve_image("boids-pyda:20261008")
    edge = f"published.{second}->published.{first}.Cleaner.clean"
    result = judge(frozen, reg.artifacts[second], tmp_path / "baseline", image, seed=71, round_=2)
    assert result["families"]["clean"]["passed"] == 6
    assert result["edges"].get(edge, {}).get("calls") == 6
    changed = judge(
        frozen, reg.artifacts[second], tmp_path / "changed", image, seed=71, round_=2, ablate_edge=edge
    )
    assert changed["edges"][edge]["mutated"] > 0
    assert changed["families"]["clean"]["passed"] < 6
    assert changed["families"]["clean"]["crashed"] == 0


def test_foreign_reexport_is_actual_service_reuse_not_host_only_call(tmp_path):
    from ecology.dynamics import service_evidence

    reg = Registry(tmp_path / "registry")
    code = """import statistics
def clean(rows, lookup, request):
    values=[r['units'] for r in rows if r.get('units') is not None]
    fill=0 if not values or request['fill']=='zero' else statistics.mean(values) if request['fill']=='mean' else statistics.median(values)
    out=[dict(r) for r in rows]
    for r in out:
        if isinstance(r.get('region'),str): r['region']=r['region'].strip().lower()
        if r.get('units') is None: r['units']=fill
    return out
"""
    first = reg.publish("a00", 1, packet(tmp_path, "one", code, {"clean": "clean"}), allowed=set())
    alias = reg.publish(
        "a01",
        2,
        packet(
            tmp_path, "two", f"from published.{first} import clean as serve\n", {"clean": "serve"}, [first]
        ),
        allowed={first},
    )
    transitive = reg.publish(
        "a02",
        3,
        packet(tmp_path, "three", f"from published.{alias} import serve\n", {"clean": "serve"}, [alias]),
        allowed={first, alias},
    )
    own = reg.publish(
        "a00",
        2,
        packet(tmp_path, "own", f"from published.{first} import clean\n", {"clean": "clean"}, [first]),
        allowed={first},
    )
    frozen = reg.freeze(tmp_path / "frozen")
    image = resolve_image("boids-pyda:20261008")
    for identity in (alias, transitive):
        baseline = judge(
            frozen, reg.artifacts[identity], tmp_path / identity / "baseline", image, seed=71, round_=3
        )
        assert baseline["families"]["clean"]["passed"] == 6
        edge = f"published.{identity}->published.{first}.clean"
        assert baseline["edges"].get(edge, {}).get("calls") == 6
        assert baseline["edges"][edge]["service_entries"] == 6
        assert all(edge in item["service_entry_edges"] for item in baseline["details"])
        assert service_evidence(baseline)["correct_cross_author_requests"] == 6
        changed = judge(
            frozen,
            reg.artifacts[identity],
            tmp_path / identity / "changed",
            image,
            seed=71,
            round_=3,
            ablate_edge=edge,
        )
        assert changed["edges"][edge]["mutated"] > 0
        assert changed["families"]["clean"]["passed"] < 6
        assert changed["families"]["clean"]["crashed"] == 0
        plain = judge(
            frozen,
            reg.artifacts[identity],
            tmp_path / identity / "plain",
            image,
            seed=71,
            round_=3,
            instrument=False,
        )
        assert plain["families"] == baseline["families"]
    own_result = judge(frozen, reg.artifacts[own], tmp_path / "own-result", image, seed=71, round_=2)
    assert own_result["families"]["clean"]["passed"] == 6
    assert service_evidence(own_result)["correct_cross_author_requests"] == 0
