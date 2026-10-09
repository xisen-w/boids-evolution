"""Native implementations of the recurring table service families."""

from statistics import median


def _base(rows, request, normalize=True):
    """Return fresh enriched rows; never mutate caller-owned data."""
    data = [dict(row) for row in rows]
    present = [row.get("units") for row in data if row.get("units") is not None]
    fill = request.get("fill", "zero")
    if not present:
        replacement = 0
    elif fill == "zero":
        replacement = 0
    elif fill == "mean":
        replacement = sum(present) / len(present)
    elif fill == "median":
        replacement = median(present)
    else:
        raise ValueError("fill must be zero, mean, or median")
    for row in data:
        if normalize:
            region = row.get("region")
            row["region"] = region.strip().lower() if isinstance(region, str) else None
        if row.get("units") is None:
            row["units"] = replacement
        units, price = row.get("units"), row.get("price_cents")
        row["revenue_cents"] = None if units is None or price is None else units * price
    return data


def clean(rows, lookup, request):
    """Normalize region and fill missing units, preserving all other fields."""
    del lookup
    data = [dict(row) for row in rows]
    present = [r.get("units") for r in data if r.get("units") is not None]
    mode = request.get("fill", "zero")
    value = 0 if not present or mode == "zero" else (sum(present) / len(present) if mode == "mean" else median(present) if mode == "median" else None)
    if value is None:
        raise ValueError("fill must be zero, mean, or median")
    for row in data:
        region = row.get("region")
        row["region"] = region.strip().lower() if isinstance(region, str) else None
        if row.get("units") is None:
            row["units"] = value
    return data


def revenue(rows, lookup, request):
    """Fill units and append revenue_cents."""
    del lookup
    return _base(rows, request, normalize=False)


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
    """Aggregate revenue by normalized region, excluding missing regions."""
    data = _base(rows, request)
    agg = request.get("agg", "sum")
    groups = {}
    for row in data:
        key = row.get("region")
        if key is not None:
            groups.setdefault(key, []).append(row["revenue_cents"])
    name = agg + "_revenue_cents"
    return [{"region": key, name: _aggregate(groups[key], agg)} for key in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    """Aggregate revenue by YYYY-MM month and normalized region."""
    data = _base(rows, request)
    agg = request.get("agg", "sum")
    groups = {}
    for row in data:
        region = row.get("region")
        date = row.get("date")
        month = date[:7] if date is not None else None
        if region is not None and month is not None:
            groups.setdefault((month, region), []).append(row["revenue_cents"])
    name = agg + "_revenue_cents"
    return [{"month": month, "region": region, name: _aggregate(groups[(month, region)], agg)}
            for month, region in sorted(groups, key=lambda pair: (str(pair[0]), str(pair[1])))]


def lookup_revenue(rows, lookup, request):
    """Append revenue and revenue per exact normalized-region target."""
    data = _base(rows, request)
    targets = {}
    for item in lookup:
        key = item.get("region")
        key = key.strip().lower() if isinstance(key, str) else None
        targets[key] = item.get("target")
    for row in data:
        target = targets.get(row.get("region"))
        rev = row["revenue_cents"]
        row["revenue_cents_per_target"] = None if rev is None or target is None or target == 0 else rev / target
    return data


def window(rows, lookup, request):
    """Append trailing-row rolling mean of nonmissing revenue."""
    data = _base(rows, request, normalize=False)
    width = request.get("window", 2)
    if width not in (2, 3, 4):
        raise ValueError("window must be 2, 3, or 4")
    for i, row in enumerate(data):
        vals = [r["revenue_cents"] for r in data[max(0, i - width + 1):i + 1] if r["revenue_cents"] is not None]
        row["roll_revenue_cents"] = sum(vals) / len(vals) if vals else None
    return data


# Conventional service check adapters (same signature as the public functions).
clean_service = clean
revenue_service = revenue
group_service = group
monthly_service = monthly
lookup_service = lookup_revenue
window_service = window
