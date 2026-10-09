"""Offline analysis contracts; these tests never run generated code or models."""

import pytest

from scripts.analyze_frozen_collection import check_aliases, dependency_closure


def test_closure_keeps_foreign_provider_behind_own_wrapper():
    cats = {
        "a00_r03": dict(author="a00", round=3, dependencies=["a00_r02"]),
        "a00_r02": dict(author="a00", round=2, dependencies=["a03_r01"]),
        "a03_r01": dict(author="a03", round=1, dependencies=[]),
    }
    closure = dependency_closure("a00_r03", cats)
    assert closure == set(cats)
    assert {cats[d]["author"] for d in closure} == {"a00", "a03"}


def test_closure_rejects_same_round_dependency():
    cats = {"x": dict(round=1, dependencies=["y"]), "y": dict(round=1, dependencies=[])}
    with pytest.raises(ValueError, match="must precede"):
        dependency_closure("x", cats)


def test_import_and_single_return_delegate_are_syntax_only():
    src = "from published.a00_r01 import clean, lookup as old\ndef lookup(rows, lookup, request):\n    return old(rows, lookup, request)\n"
    assert check_aliases(src, {"clean": "clean", "lookup": "lookup"}) == (["clean"], ["lookup"])


def test_overwritten_import_is_not_direct_adapter():
    src = "from published.a00_r01 import clean\ndef clean(rows, lookup, request):\n    return rows\n"
    assert check_aliases(src, {"clean": "clean"}) == ([], [])
    src = "from published.a00_r01 import clean\nclean = lambda rows, lookup, request: rows\n"
    assert check_aliases(src, {"clean": "clean"}) == ([], [])


def test_extra_statements_are_not_single_return_delegate():
    src = "from published.a00_r01 import clean as old\ndef clean(rows, lookup, request):\n    rows = list(rows)\n    return old(rows, lookup, request)\n"
    assert check_aliases(src, {"clean": "clean"}) == ([], [])
