from studies.tool_ecology.scripts.frozen_audit import structural_coverage


def test_author_removal_propagates_transitive_dependencies():
    cards = [
        dict(id="a00_r01", author="a00", dependencies=[]),
        dict(id="a01_r02", author="a01", dependencies=["a00_r01"]),
        dict(id="a02_r03", author="a02", dependencies=["a01_r02"]),
        dict(id="a03_r01", author="a03", dependencies=[]),
    ]
    passing = {"a00_r01": ["revenue"], "a01_r02": ["group"], "a02_r03": ["monthly"], "a03_r01": ["clean"]}
    got = structural_coverage(cards, passing)
    assert got["all_families"] == ["clean", "group", "monthly", "revenue"]
    assert got["after_author_removal"]["a00"] == ["clean"]
    assert got["after_author_removal"]["a01"] == ["clean", "revenue"]
    assert got["after_author_removal"]["a03"] == ["group", "monthly", "revenue"]
    assert got["coverage_loss"]["a00"] == 3


def test_redundant_generalist_is_not_a_unique_coverage_contributor():
    cards = [
        dict(id="a00_r01", author="a00", dependencies=[]),
        dict(id="a01_r01", author="a01", dependencies=[]),
    ]
    got = structural_coverage(cards, {"a00_r01": ["clean", "revenue"], "a01_r01": ["clean", "revenue"]})
    assert got["coverage_loss"] == {"a00": 0, "a01": 0}


def test_wrapping_a_neighbor_does_not_become_self_contained_competence():
    cards = [
        dict(id="a00_r01", author="a00", dependencies=[]),
        dict(id="a01_r01", author="a01", dependencies=[]),
        dict(id="a01_r02", author="a01", dependencies=["a00_r01"]),
        dict(id="a01_r03", author="a01", dependencies=["a01_r02"]),
        dict(id="a02_r01", author="a02", dependencies=[]),
        dict(id="a02_r02", author="a02", dependencies=["a02_r01"]),
    ]
    passing = {
        "a00_r01": ["clean"],
        "a01_r01": ["revenue"],
        "a01_r02": ["clean", "revenue", "monthly"],
        "a01_r03": ["window"],
        "a02_r01": ["group"],
        "a02_r02": ["lookup"],
    }
    got = structural_coverage(cards, passing)
    assert got["self_contained_author_profiles"] == {
        "a00": ["clean"],
        "a01": ["revenue"],
        "a02": ["group", "lookup"],
    }
    assert got["best_self_contained_author_coverage"] == 2
    assert got["collective_minus_best_self_contained_coverage"] == 4
