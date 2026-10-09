import copy

from ecology import workload


def test_revenue_group_requires_new_column_and_normalization():
    rows = [
        dict(region=" North ", units=None, price_cents=100),
        dict(region="north", units=2, price_cents=300),
    ]
    request = dict(fill="zero", agg="sum", window=2)
    original = copy.deepcopy(rows)
    assert workload.reference("group", rows, [], request) == [dict(region="north", sum_revenue_cents=600)]
    assert rows == original


def test_lookup_uses_derived_revenue_and_handles_zero_and_unknown_targets():
    rows = [
        dict(region=" North ", units=2, price_cents=100),
        dict(region="south", units=1, price_cents=100),
        dict(region="moon", units=1, price_cents=100),
    ]
    lookup = [dict(region="north", target=10), dict(region="south", target=0)]
    got = workload.reference("lookup", rows, lookup, dict(fill="zero", agg="sum", window=2))
    assert [x["revenue_cents_per_target"] for x in got] == [20, None, None]


def test_private_cases_reproducible_and_different_across_rounds():
    a = workload.cases(71, 1, "clean", count=6)
    assert a == workload.cases(71, 1, "clean", count=6)
    assert a != workload.cases(71, 2, "clean", count=6)
    assert {x["request"]["fill"] for x in a} == {"zero", "mean", "median"}
    assert all("expected" not in x for x in a)


def test_each_family_has_real_nontrivial_reference_on_all_cases():
    for family in workload.FAMILIES:
        batch = workload.cases(71, 1, family, count=6)
        outputs = [workload.reference(family, x["rows"], x["lookup"], x["request"]) for x in batch]
        assert all(isinstance(y, list) for y in outputs)
        assert any(y != x["rows"] for x, y in zip(batch, outputs))


def test_mean_fill_cannot_be_replaced_by_zero_in_group_or_monthly():
    for family in ("group", "monthly"):
        panel = workload.cases(71, 1, family, count=6)
        distinguished = []
        for case in panel:
            if case["request"]["fill"] == "mean":
                wrong = {**case["request"], "fill": "zero"}
                expected = workload.reference(family, case["rows"], case["lookup"], case["request"])
                incorrect = workload.reference(family, case["rows"], case["lookup"], wrong)
                distinguished.append(expected != incorrect)
        assert any(distinguished)


def test_equality_honors_absolute_tolerance_and_rejects_large_errors():
    assert workload.equal([{"x": 2.0000009}], [{"x": 2.0}])
    assert not workload.equal([{"x": 2.000002}], [{"x": 2.0}])
    assert not workload.equal([{"x": True}], [{"x": 1.0}])


def test_mean_aggregation_has_nonempty_unequal_positive_revenues():
    for family in ("group", "monthly"):
        panel = workload.cases(71, 1, family)
        witnessed = False
        for case in panel:
            if case["request"]["agg"] == "mean":
                expected = workload.reference(family, case["rows"], case["lookup"], case["request"])
                summed = workload.reference(
                    family, case["rows"], case["lookup"], {**case["request"], "agg": "sum"}
                )
                for actual, wrong in zip(expected, summed):
                    value = actual["mean_revenue_cents"]
                    if value is not None and value > 0 and value != wrong["sum_revenue_cents"]:
                        witnessed = True
        assert witnessed
