"""Host-only exploratory DEV service workloads; never mounted into agents."""

import copy
import hashlib
import math
import random

from boidsnet.env import mechenv as ref

FAMILIES = {
    "clean": "Normalize region strings by strip/lower; fill missing units using request.fill (zero/mean/median, all-missing -> 0). Preserve all columns and row order.",
    "revenue": "Fill missing units using request.fill; derive revenue_cents=units*price_cents, None if either operand missing. Preserve original columns/order.",
    "group": "Normalize region and derive revenue as in revenue; group by region, dropping missing keys. Aggregate nonmissing revenue with request.agg (sum/mean/count); output region and <agg>_revenue_cents, sorted by str(region). Empty groups yield 0 for sum/count and None for mean.",
    "monthly": "Normalize region, derive revenue as in revenue, add month=date[:7] (None if missing); group by month AND region, dropping any missing group key. Aggregate as request.agg; output month, region, <agg>_revenue_cents, sorted lexicographically by stringified keys.",
    "lookup": "Normalize region and derive revenue as in revenue. Add revenue_cents_per_target = revenue_cents / target from exact region-key lookup. Unknown region, zero/None target or None revenue -> None. Preserve all original/derived columns/order; do not add target/manager.",
    "window": "Derive revenue as in revenue, then add roll_revenue_cents: mean of nonmissing revenue in the trailing request.window ROWS including current (not last nonmissing rows); None if window has no values. Preserve columns/order.",
}


def reference(family, rows, lookup, request):
    rows, lookup = copy.deepcopy(rows), copy.deepcopy(lookup)
    if family in {"clean", "group", "monthly", "lookup"}:
        rows = ref.p_normalize_str(rows, lookup, col="region")
    rows = ref.p_fill_missing(rows, lookup, col="units", strategy=request["fill"])
    if family == "clean":
        return rows
    rows = ref.p_derive(rows, lookup, new="revenue_cents", a="units", op="*", b="price_cents")
    if family == "revenue":
        return rows
    if family == "group":
        return ref.p_group_agg(rows, lookup, key="region", col="revenue_cents", agg=request["agg"])
    if family == "monthly":
        rows = ref.p_month_bucket(rows, lookup, col="date")
        return ref.p_multi_group_agg(
            rows, lookup, keys=["month", "region"], col="revenue_cents", agg=request["agg"]
        )
    if family == "lookup":
        return ref.p_lookup_ratio(rows, lookup, col="revenue_cents")
    if family == "window":
        return ref.p_rolling_mean(rows, lookup, col="revenue_cents", window=request["window"])
    raise ValueError(f"unknown family {family}")


def cases(seed, round_, family, count=6):
    if family not in FAMILIES or count < 1:
        raise ValueError("unknown family or empty case set")
    value = int.from_bytes(hashlib.sha256(f"v0.3:{seed}:{round_}:{family}".encode()).digest()[:8], "big")
    rng = random.Random(value)
    result = []
    for i in range(count):
        data_seed = rng.randrange(1_000_000, 2_000_000)
        rows, lookup = ref.gen_table(data_seed, n_rows=9), ref.gen_lookup(data_seed)
        if i % 6 == 1:
            for row in rows:
                row["units"] = None
        if i % 6 == 2:
            rows = []
        if i % 6 == 3:
            lookup[0]["target"] = 0
            rows[0].update(region=" North ", units=2, price_cents=100)
            rows[1].update(region="moon", units=1, price_cents=100)
            rows[2].update(region=None, units=1, price_cents=None)
        if i % 6 == 4:
            for row in rows:
                row["price_cents"] = None
        if i % 6 in (0, 5):
            rows[0].update(units=None, price_cents=100)
            rows[1].update(units=2, price_cents=300)
            rows[2].update(units=4, price_cents=200)
            rows[3].update(units=8, price_cents=150)
            for row in rows[:4]:
                row.update(region=" North ", date="2025-01-03")
            rows[4].update(region="north", date="2025-01-03", price_cents=None)
        request = dict(
            fill=["mean", "median", "zero", "zero", "mean", "median"][i % 6],
            agg=["mean", "sum", "count", "sum", "mean", "count"][i % 6],
            window=[2, 3, 4][i % 3],
        )
        result.append(dict(rows=rows, lookup=lookup, request=request))
    return result


def equal(got, expected):
    if not isinstance(got, list) or len(got) != len(expected):
        return False
    for actual, desired in zip(got, expected):
        if not isinstance(actual, dict) or set(actual) != set(desired):
            return False
        for key, value in desired.items():
            observed = actual[key]
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if (
                    isinstance(observed, bool)
                    or not isinstance(observed, (int, float))
                    or not math.isclose(observed, value, rel_tol=0, abs_tol=1e-6)
                ):
                    return False
            elif observed != value:
                return False
    return True
