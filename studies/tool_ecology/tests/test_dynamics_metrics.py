from ecology.dynamics_metrics import summarize


def event(author, round_, families, cross=()):
    return dict(
        author=author,
        round=round_,
        publication_status="published",
        id=f"{author}_r{round_:02d}",
        verified_families=families,
        cross_author_edges=list(cross),
        verified_cross_author_edges=list(cross),
    )


def test_specialization_requires_three_verified_consecutive_rounds_and_unique_family():
    rows = [event("a00", i, ["clean"]) for i in range(1, 4)]
    rows += [event("a01", i, ["clean", "revenue"]) for i in range(1, 4)]
    rows += [event("a02", 1, ["group"]), event("a02", 2, []), event("a02", 3, ["group"])]
    got = summarize(rows)
    assert got["sustained_specialists"] == [
        {"author": "a00", "family": "clean", "start_round": 1, "end_round": 3}
    ]
    assert got["verified_family_coverage"] == ["clean", "group", "revenue"]
    assert got["redundant_author_family_pairs"] == 1


def test_static_claims_and_unverified_edges_do_not_become_capabilities():
    rows = [event("a00", 1, []), event("a01", 1, ["clean"], ["published.a01_r01->published.a00_r01.value"])]
    got = summarize(rows)
    assert got["verified_family_coverage"] == ["clean"]
    assert got["correct_cross_author_publications"] == 1
    assert got["sustained_specialists"] == []
