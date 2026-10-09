"""Reusable row-oriented table transforms for the six publication service families."""
from statistics import median


def _fill(rows, request):
    mode = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero' or not vals:
        value = 0
    elif mode == 'mean':
        value = sum(vals) / len(vals)
    elif mode == 'median':
        value = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [dict(r, units=value if r.get('units') is None else r.get('units')) for r in rows]


def _region(v):
    return v.strip().lower() if isinstance(v, str) else v


def _base(rows, request, normalize=True):
    out = _fill(rows, request)
    for r in out:
        if normalize:
            r['region'] = _region(r.get('region'))
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    out = _fill(rows, request)
    for r in out:
        r['region'] = _region(r.get('region'))
    return out


def revenue(rows, lookup, request):
    return _base(rows, request, normalize=False)


def _aggregate(values, agg):
    values = [v for v in values if v is not None]
    if agg == 'sum': return sum(values)
    if agg == 'count': return len(values)
    if agg == 'mean': return sum(values) / len(values) if values else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def _groups(records, keys, request):
    agg = request.get('agg', 'sum')
    buckets = {}
    for r in records:
        key = tuple(r.get(k) for k in keys)
        if any(v is None for v in key):
            continue
        buckets.setdefault(key, []).append(r.get('revenue_cents'))
    name = agg + '_revenue_cents'
    # Sorting by stringified keys; stable tie-breaking handles unlike comparable types.
    result = [{**dict(zip(keys, key)), name: _aggregate(vals, agg)} for key, vals in buckets.items()]
    result.sort(key=lambda r: tuple(str(r[k]) for k in keys))
    return result


def group(rows, lookup, request):
    return _groups(_base(rows, request), ('region',), request)


def monthly(rows, lookup, request):
    records = _base(rows, request)
    for r in records:
        date = r.get('date')
        r['month'] = date[:7] if date is not None else None
    return _groups(records, ('month', 'region'), request)


def lookup(rows, lookup, request):
    records = _base(rows, request)
    targets = {}
    for item in lookup:
        key = _region(item.get('region'))
        targets[key] = item.get('target')
    for r in records:
        target = targets.get(r.get('region'))
        rev = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return records


def window(rows, lookup, request):
    records = _base(rows, request, normalize=False)
    width = request.get('window')
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(records):
        vals = [x['revenue_cents'] for x in records[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return records
