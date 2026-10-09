"""Native table transformations for the six recurring service families."""
from statistics import mean, median


def _missing(x):
    return x is None


def _base(rows, request):
    """Copy rows, normalize region, fill units, then derive revenue."""
    out = [dict(row) for row in rows]
    fill = request.get("fill", "zero")
    present = [r.get("units") for r in out if not _missing(r.get("units"))]
    if fill == "zero":
        replacement = 0
    elif fill == "mean":
        replacement = mean(present) if present else 0
    elif fill == "median":
        replacement = median(present) if present else 0
    else:
        raise ValueError("fill must be zero, mean, or median")
    for r in out:
        region = r.get("region")
        r["region"] = region.strip().lower() if isinstance(region, str) else region
        if _missing(r.get("units")):
            r["units"] = replacement
        units, price = r.get("units"), r.get("price_cents")
        r["revenue_cents"] = None if units is None or price is None else units * price
    return out


def clean(rows, lookup, request):
    return _base(rows, request)


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(values, agg):
    valid = [v for v in values if v is not None]
    if agg == "sum":
        return sum(valid)
    if agg == "count":
        return len(valid)
    if agg == "mean":
        return sum(valid) / len(valid) if valid else None
    raise ValueError("agg must be sum, mean, or count")


def group(rows, lookup, request):
    data = _base(rows, request)
    groups = {}
    for r in data:
        key = r.get("region")
        if key is not None:
            groups.setdefault(key, []).append(r.get("revenue_cents"))
    agg = request.get("agg", "sum")
    return [{"region": k, agg + "_revenue_cents": _aggregate(groups[k], agg)}
            for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    data = _base(rows, request)
    groups = {}
    for r in data:
        region = r.get("region")
        date = r.get("date")
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r.get("revenue_cents"))
    agg = request.get("agg", "sum")
    return [{"month": m, "region": r, agg + "_revenue_cents": _aggregate(groups[(m, r)], agg)}
            for m, r in sorted(groups, key=lambda k: (str(k[0]), str(k[1])))]


def lookup(rows, lookup, request):
    data = _base(rows, request)
    targets = {r.get("region"): r.get("target") for r in lookup}
    for r in data:
        target = targets.get(r.get("region"))
        revenue_value = r.get("revenue_cents")
        r["revenue_cents_per_target"] = (None if target is None or target == 0 or revenue_value is None
                                            else revenue_value / target)
    return data


def window(rows, lookup, request):
    data = _base(rows, request)
    n = request.get("window")
    if n not in (2, 3, 4):
        raise ValueError("window must be 2, 3, or 4")
    values = []
    for i, r in enumerate(data):
        values.append(r.get("revenue_cents"))
        valid = [x for x in values[max(0, i + 1 - n):i + 1] if x is not None]
        r["roll_revenue_cents"] = sum(valid) / len(valid) if valid else None
    return data
