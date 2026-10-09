"""Native implementations of the tabular services."""
from statistics import mean, median

_MISSING = object()

def _filled(rows, request):
    """Copy rows and fill missing units without changing input objects."""
    mode = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero' or not vals:
        value = 0
    elif mode == 'mean':
        value = mean(vals)
    elif mode == 'median':
        value = median(vals)
    else:
        raise ValueError("fill must be zero, mean, or median")
    result = []
    for row in rows:
        out = dict(row)
        if out.get('units') is None:
            out['units'] = value
        yield out

def _normalize(row):
    region = row.get('region')
    return region.strip().lower() if isinstance(region, str) else region

def _base(rows, request, normalize=False):
    out = list(_filled(rows, request))
    for row in out:
        if normalize:
            row['region'] = _normalize(row)
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return out

def clean(rows, lookup, request):
    out = list(_filled(rows, request))
    for row in out:
        row['region'] = _normalize(row)
    return out

def revenue(rows, lookup, request):
    return _base(rows, request)

def _aggregate(values, agg):
    vals = [x for x in values if x is not None]
    if agg == 'sum':
        return sum(vals)
    if agg == 'count':
        return len(vals)
    if agg == 'mean':
        return sum(vals) / len(vals) if vals else None
    raise ValueError("agg must be sum, mean, or count")

def group(rows, lookup, request):
    data = _base(rows, request, True)
    groups = {}
    for r in data:
        key = r.get('region')
        if key is not None:
            groups.setdefault(key, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': key, agg + '_revenue_cents': _aggregate(groups[key], agg)}
            for key in sorted(groups, key=str)]

def monthly(rows, lookup, request):
    data = _base(rows, request, True)
    groups = {}
    for r in data:
        month = r.get('date')
        month = month[:7] if month is not None else None
        region = r.get('region')
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': reg, agg + '_revenue_cents': _aggregate(groups[(m, reg)], agg)}
            for m, reg in sorted(groups, key=lambda key: (str(key[0]), str(key[1])))]

def lookup(rows, lookup, request):
    out = _base(rows, request, True)
    targets = {r.get('region'): r.get('target') for r in lookup}
    for row in out:
        target = targets.get(row.get('region'))
        revenue_value = row['revenue_cents']
        row['revenue_cents_per_target'] = (None if target is None or target == 0 or revenue_value is None
                                           else revenue_value / target)
    return out

def window(rows, lookup, request):
    out = _base(rows, request)
    n = request.get('window', 2)
    if n not in (2, 3, 4):
        raise ValueError("window must be 2, 3, or 4")
    vals = []
    for i, row in enumerate(out):
        vals.append(row['revenue_cents'])
        trailing = [x for x in vals[max(0, i + 1 - n):i + 1] if x is not None]
        row['roll_revenue_cents'] = sum(trailing) / len(trailing) if trailing else None
    return out

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
