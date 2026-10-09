import json

import pytest

from ecology.registry import LocalSociety, Registry


def candidate(tmp_path, name, deps=(), code="def value(): return 3\n"):
    p = tmp_path / name
    p.mkdir()
    (p / "__init__.py").write_text(code)
    (p / "README.md").write_text("Use value().")
    (p / "publish.json").write_text(
        json.dumps(dict(description=name, capabilities=["arithmetic"], dependencies=list(deps)))
    )
    return p


def test_snapshot_and_bundle_receipts(tmp_path):
    registry = Registry(tmp_path / "registry")
    society = LocalSociety(registry, 4, "local-neutral", seed=0)
    first = registry.publish("a00", 1, candidate(tmp_path, "one"), allowed=set())
    assert society.view("a01", 1) == set()
    society.deliver(1, [first])
    neighbors = society.neighbors("a00")
    for a in neighbors:
        assert first in society.view(a, 2)
    nonneighbor = next(a for a in society.agents if a != "a00" and a not in neighbors)
    assert first not in society.view(nonneighbor, 2)
    author = neighbors[0]
    second = registry.publish(
        author,
        2,
        candidate(
            tmp_path, "two", [first], f"from published.{first} import value\ndef result(): return value()+1\n"
        ),
        allowed=society.view(author, 2),
    )
    assert second not in society.view("a00", 2)
    society.deliver(2, [second])
    assert {first, second} <= society.view("a00", 3)
    assert any(x["member"] == first and x["root"] == second for x in society.receipts)


def test_rejects_unknown_import_overwrite_and_symlink(tmp_path):
    registry = Registry(tmp_path / "registry")
    p = candidate(tmp_path, "one", ["a99_r01"])
    with pytest.raises(ValueError, match="unreceived"):
        registry.publish("a00", 1, p, allowed=set())
    (p / "publish.json").write_text(json.dumps(dict(description="x", capabilities=[], dependencies=[])))
    registry.publish("a00", 1, p, allowed=set())
    with pytest.raises(ValueError, match="exists"):
        registry.publish("a00", 1, p, allowed=set())
    q = candidate(tmp_path, "two")
    (q / "leak.py").symlink_to(p / "__init__.py")
    with pytest.raises(ValueError, match="symlink"):
        registry.publish("a01", 1, q, allowed=set())


def test_independent_and_frozen_tamper_detection(tmp_path):
    registry = Registry(tmp_path / "registry")
    society = LocalSociety(registry, 4, "independent", seed=0)
    tool = registry.publish("a00", 1, candidate(tmp_path, "one"), allowed=set())
    society.deliver(1, [tool])
    assert society.view("a01", 2) == set()
    frozen = registry.freeze(tmp_path / "frozen")
    registry.verify_freeze(frozen)
    (frozen / "published" / tool / "__init__.py").write_text("oops")
    with pytest.raises(ValueError, match="hash"):
        registry.verify_freeze(frozen)


def test_candidate_root_and_host_ingestion_reject_symlinks(tmp_path):
    from ecology.registry import file_hashes

    registry = Registry(tmp_path / "registry")
    real = candidate(tmp_path, "real")
    alias = tmp_path / "alias"
    alias.symlink_to(real, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        registry.publish("a00", 1, alias, allowed=set())
    (real / "host.py").symlink_to("/etc/passwd")
    with pytest.raises(ValueError, match="symlink"):
        file_hashes(real)


def test_from_published_import_requires_declared_dependency(tmp_path):
    registry = Registry(tmp_path / "registry")
    one = registry.publish("a00", 1, candidate(tmp_path, "one"), allowed=set())
    other = candidate(
        tmp_path, "other", code=f"from published import {one}\ndef result(): return {one}.value()\n"
    )
    with pytest.raises(ValueError, match="undeclared"):
        registry.publish("a01", 2, other, allowed={one})


@pytest.mark.parametrize("code", ["from .. import a00_r01", "from ..a00_r01 import value"])
def test_relative_import_cannot_escape_publication(tmp_path, code):
    registry = Registry(tmp_path / "registry")
    one = registry.publish("a00", 1, candidate(tmp_path, "one"), allowed=set())
    other = candidate(tmp_path, "other", code=code)
    with pytest.raises(ValueError, match="relative import escapes"):
        registry.publish("a01", 2, other, allowed={one})


def test_nested_internal_relative_imports_are_allowed(tmp_path):
    registry = Registry(tmp_path / "registry")
    p = candidate(tmp_path, "nested", code="from .sub import value\n")
    (p / "sub").mkdir()
    (p / "sub/__init__.py").write_text("from ..base import value\n")
    (p / "sub/helper.py").write_text("from ..base import value\n")
    (p / "base.py").write_text("def value(): return 3\n")
    registry.publish("a00", 1, p, allowed=set())


def test_checks_are_preserved_and_invalid_callable_rejected(tmp_path):
    registry = Registry(tmp_path / "registry")
    p = candidate(tmp_path, "checked")
    meta = json.loads((p / "publish.json").read_text())
    meta["checks"] = {"clean": "value"}
    (p / "publish.json").write_text(json.dumps(meta))
    identity = registry.publish("a00", 1, p, allowed=set())
    assert registry.artifacts[identity]["checks"] == {"clean": "value"}
    q = candidate(tmp_path, "invalid-check")
    meta["checks"] = {"clean": "os.system"}
    (q / "publish.json").write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="checks"):
        registry.publish("a01", 1, q, allowed=set())


@pytest.mark.parametrize("manifest", [[], None, 42])
def test_non_object_manifest_is_rejected_as_contract_failure(tmp_path, manifest):
    registry = Registry(tmp_path / "registry")
    p = candidate(tmp_path, "nonobject")
    (p / "publish.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="manifest"):
        registry.publish("a00", 1, p, allowed=set())
