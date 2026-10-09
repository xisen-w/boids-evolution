"""Native implementations of the tabular service families."""


def _fill_units(rows, request):
    fill = request.get("fill", "zero")
    values = [r.get("units") for r in rows if r.get("units") is not None]
    if fill == "zero" or not values:
        replacement = 0
    elif fill == "mean":
        replacement = sum(values) / len(values)
    elif fill == "median":
        ordered = sorted(values)
        n = len(ordered)
        replacement = ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    else:
        raise ValueError("fill must be zero, mean, or median")
    return [dict(r, units=(replacement if r.get("units") is None else r.get("units"))) for r in rows]


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _revenue_rows(rows, request):
    result = _fill_units(rows, request)
    for row in result:
        units, price = row.get("units"), row.get("price_cents")
        row["revenue_cents"] = None if units is None or price is None else units * price
    return result


def clean(rows, lookup, request):
    result = _fill_units(rows, request)
    for row in result:
        row["region"] = _region(row.get("region"))
    return result


def revenue(rows, lookup, request):
    return _revenue_rows(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == "sum":
        return sum(present)
    if agg == "count":
        return len(present)
    if agg == "mean":
        return sum(present) / len(present) if present else None
    raise ValueError("agg must be sum, mean, or count")


def group(rows, lookup, request):
    data = _revenue_rows(rows, request)
    groups = {}
    for row in data:
        region = _region(row.get("region"))
        if region is not None:
            groups.setdefault(region, []).append(row["revenue_cents"])
    agg = request.get("agg", "sum")
    key = agg + "_revenue_cents"
    return [{"region": region, key: _aggregate(groups[region], agg)}
            for region in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    data = _revenue_rows(rows, request)
    groups = {}
    for row in data:
        region = _region(row.get("region"))
        date = row.get("date")
        month = date[:7] if date is not None else None
        if region is not None and month is not None:
            groups.setdefault((month, region), []).append(row["revenue_cents"])
    agg = request.get("agg", "sum")
    key = agg + "_revenue_cents"
    return [{"month": month, "region": region, key: _aggregate(groups[(month, region)], agg)}
            for month, region in sorted(groups, key=lambda x: (str(x[0]), str(x[1])))]


def lookup(rows, lookup, request):
    data = _revenue_rows(rows, request)
    targets = {_region(item.get("region")): item.get("target") for item in lookup}
    for row in data:
        region, target, amount = _region(row.get("region")), None, row.get("revenue_cents")
        if region in targets:
            target = targets[region]
        row["revenue_cents_per_target"] = (amount / target if amount is not None and target not in (None, 0) else None)
    return data


def window(rows, lookup, request):
    data = _revenue_rows(rows, request)
    width = request.get("window", 2)
    if width not in (2, 3, 4):
        raise ValueError("window must be 2, 3, or 4")
    for i, row in enumerate(data):
        values = [r["revenue_cents"] for r in data[max(0, i - width + 1):i + 1] if r["revenue_cents"] is not None]
        row["roll_revenue_cents"] = sum(values) / len(values) if values else None
    return data
