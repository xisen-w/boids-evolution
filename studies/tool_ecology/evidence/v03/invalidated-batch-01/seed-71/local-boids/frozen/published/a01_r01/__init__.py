"""Native implementations of the recurring tabular service families."""
from statistics import median


def _filled(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero' or not vals:
        replacement = 0
    elif mode == 'mean':
        replacement = sum(vals) / len(vals)
    elif mode == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be zero, mean, or median")
    result = []
    for row in rows:
        out = dict(row)
        if out.get('units') is None:
            out['units'] = replacement
        result.append(out)
    return result


def _normalized(rows, request):
    result = _filled(rows, request)
    for row in result:
        region = row.get('region')
        row['region'] = region.strip().lower() if isinstance(region, str) else region
    return result


def _revenue(rows, request):
    result = _filled(rows, request)
    for row in result:
        u, p = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if u is None or p is None else u * p
    return result


def clean(rows, lookup, request):
    return _normalized(rows, request)


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(present)
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return sum(present) / len(present) if present else None
    raise ValueError("agg must be sum, mean, or count")


def _groups(records, keys, agg):
    buckets = {}
    for r in records:
        key = tuple(r.get(k) for k in keys)
        if any(v is None for v in key):
            continue
        buckets.setdefault(key, []).append(r['revenue_cents'])
    suffix = f'{agg}_revenue_cents'
    result = [dict(zip(keys, key), **{suffix: _aggregate(vals, agg)}) for key, vals in buckets.items()]
    result.sort(key=lambda r: tuple(str(r[k]) for k in keys))
    return result


def group(rows, lookup, request):
    return _groups(_normalized(_revenue(rows, request), request), ['region'], request.get('agg', 'sum'))


def monthly(rows, lookup, request):
    records = _normalized(_revenue(rows, request), request)
    for r in records:
        date = r.get('date')
        r['month'] = date[:7] if date is not None else None
    return _groups(records, ['month', 'region'], request.get('agg', 'sum'))


def lookup(rows, lookup, request):
    records = _normalized(_revenue(rows, request), request)
    targets = {}
    for item in lookup:
        key = item.get('region')
        key = key.strip().lower() if isinstance(key, str) else key
        targets[key] = item.get('target')
    for r in records:
        target, rev = targets.get(r.get('region')), r.get('revenue_cents')
        r['revenue_cents_per_target'] = rev / target if target not in (None, 0) and rev is not None else None
    return records


def window(rows, lookup, request):
    records = _revenue(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(records):
        vals = [x['revenue_cents'] for x in records[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return records
