"""Reusable table transformations for the six publication service families."""
from statistics import mean, median


def _base(rows, request):
    """Copy rows, normalize region, fill missing units, derive revenue."""
    out = [dict(row) for row in rows]
    missing = [r.get('units') is None for r in out]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    fill = request.get('fill', 'zero')
    if fill == 'mean':
        replacement = mean(vals) if vals else 0
    elif fill == 'median':
        replacement = median(vals) if vals else 0
    else:
        replacement = 0
    for i, row in enumerate(out):
        region = row.get('region')
        row['region'] = region.strip().lower() if isinstance(region, str) else region
        if missing[i]:
            row['units'] = replacement
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return out


def clean(rows, lookup, request):
    """Normalize regions and fill units; preserve other fields and row order."""
    out = [dict(r) for r in rows]
    missing = [r.get('units') is None for r in out]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    f = request.get('fill', 'zero')
    x = (mean(vals) if vals else 0) if f == 'mean' else (median(vals) if vals else 0) if f == 'median' else 0
    for i, r in enumerate(out):
        region = r.get('region')
        r['region'] = region.strip().lower() if isinstance(region, str) else region
        if missing[i]: r['units'] = x
    return out


def revenue(rows, lookup, request):
    """Fill units and add revenue_cents, retaining input columns/order."""
    return _base(rows, request)


def _aggregate(values, agg):
    vals = [x for x in values if x is not None]
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals) / len(vals) if vals else None
    return sum(vals)


def group(rows, lookup, request):
    """Group normalized regions and aggregate nonmissing revenue."""
    agg = request.get('agg', 'sum')
    buckets = {}
    for r in _base(rows, request):
        key = r.get('region')
        if key is not None: buckets.setdefault(key, []).append(r.get('revenue_cents'))
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(buckets[k], agg)}
            for k in sorted(buckets, key=str)]


def monthly(rows, lookup, request):
    """Group by YYYY-MM and normalized region, omitting missing keys."""
    agg = request.get('agg', 'sum')
    buckets = {}
    for r in _base(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            buckets.setdefault((month, region), []).append(r.get('revenue_cents'))
    keys = sorted(buckets, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(buckets[(m,r)], agg)} for m,r in keys]


def lookup(rows, lookup, request):
    """Add revenue per exact region-key target; lookup fields are not emitted."""
    targets = {x.get('region'): x.get('target') for x in lookup}
    out = _base(rows, request)
    for r in out:
        target = targets.get(r.get('region'))
        value = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value / target
    return out


def window(rows, lookup, request):
    """Add trailing physical-row mean of nonmissing revenue."""
    out = _base(rows, request)
    w = request.get('window', 2)
    revenues = [r.get('revenue_cents') for r in out]
    for i, r in enumerate(out):
        vals = [x for x in revenues[max(0, i-w+1):i+1] if x is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
