"""Native implementations for common row-table service transformations."""
from statistics import mean, median


def _filled(rows, request):
    """Copy rows, normalize region, and fill missing units."""
    out = []
    missing = [r.get("units") for r in rows if r.get("units") is not None]
    mode = request.get("fill", "zero")
    if not missing:
        replacement = 0
    elif mode == "zero":
        replacement = 0
    elif mode == "mean":
        replacement = mean(missing)
    elif mode == "median":
        replacement = median(missing)
    else:
        raise ValueError("fill must be zero, mean, or median")
    for row in rows:
        item = dict(row)
        region = item.get("region")
        item["region"] = region.strip().lower() if isinstance(region, str) else region
        if item.get("units") is None:
            item["units"] = replacement
        out.append(item)
    return out


def _revenue(rows, request):
    out = _filled(rows, request)
    for row in out:
        units, price = row.get("units"), row.get("price_cents")
        row["revenue_cents"] = None if units is None or price is None else units * price
    return out


def clean(rows, lookup, request):
    return _filled(rows, request)


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == "sum":
        return sum(vals)
    if agg == "count":
        return len(vals)
    if agg == "mean":
        return sum(vals) / len(vals) if vals else None
    raise ValueError("agg must be sum, mean, or count")


def group(rows, lookup, request):
    data = _revenue(rows, request)
    groups = {}
    for row in data:
        key = row.get("region")
        if key is not None:
            groups.setdefault(key, []).append(row.get("revenue_cents"))
    agg = request.get("agg", "sum")
    return [{"region": key, f"{agg}_revenue_cents": _aggregate(groups[key], agg)}
            for key in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    data = _revenue(rows, request)
    groups = {}
    for row in data:
        region, date = row.get("region"), row.get("date")
        month = date[:7] if date is not None else None
        if region is not None and month is not None:
            groups.setdefault((month, region), []).append(row.get("revenue_cents"))
    agg = request.get("agg", "sum")
    keys = sorted(groups, key=lambda k: (str(k[0]), str(k[1])))
    return [{"month": m, "region": r, f"{agg}_revenue_cents": _aggregate(groups[(m, r)], agg)}
            for m, r in keys]


def lookup(rows, lookup, request):
    out = _revenue(rows, request)
    targets = {item.get("region"): item.get("target") for item in lookup}
    for row in out:
        region, rev = row.get("region"), row.get("revenue_cents")
        target = targets.get(region)
        row["revenue_cents_per_target"] = None if rev is None or target in (None, 0) else rev / target
    return out


def window(rows, lookup, request):
    out = _revenue(rows, request)
    size = request.get("window", 2)
    if size not in (2, 3, 4):
        raise ValueError("window must be 2, 3, or 4")
    for i, row in enumerate(out):
        vals = [r["revenue_cents"] for r in out[max(0, i-size+1):i+1] if r["revenue_cents"] is not None]
        row["roll_revenue_cents"] = sum(vals) / len(vals) if vals else None
    return out
