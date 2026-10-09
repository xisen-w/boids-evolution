"""Reusable implementations of the tabular service families."""
from statistics import median


def _fill_values(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero':
        replacement = 0
    elif not vals:
        replacement = 0
    elif mode == 'mean':
        replacement = sum(vals) / len(vals)
    elif mode == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be zero, mean, or median")
    return [dict(r, units=(replacement if r.get('units') is None else r.get('units'))) for r in rows]


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _base(rows, request):
    out = _fill_values(rows, request.get('fill', 'zero'))
    for row in out:
        row['region'] = _region(row.get('region'))
        u, p = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    out = _fill_values(rows, request.get('fill', 'zero'))
    for row in out:
        row['region'] = _region(row.get('region'))
    return out


def _revenue_rows(rows, request):
    out = _fill_values(rows, request.get('fill', 'zero'))
    for row in out:
        u, p = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if u is None or p is None else u * p
    return out


def revenue(rows, lookup, request):
    return _revenue_rows(rows, request)


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals) / len(vals) if vals else None
    raise ValueError('agg must be sum, mean, or count')


def group(rows, lookup, request):
    groups = {}
    for r in _base(rows, request):
        k = r['region']
        if k is not None: groups.setdefault(k, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    key = agg + '_revenue_cents'
    return [{'region': k, key: _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    groups = {}
    for r in _base(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum'); key = agg + '_revenue_cents'
    return [{'month': m, 'region': r, key: _aggregate(groups[(m,r)], agg)}
            for m,r in sorted(groups, key=lambda x: (str(x[0]), str(x[1])))]


def lookup(rows, lookup, request):
    out = _base(rows, request)
    targets = {_region(x.get('region')): x.get('target') for x in lookup}
    for r in out:
        target = targets.get(r.get('region'))
        rev = r['revenue_cents']
        r['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return out


def window(rows, lookup, request):
    out = _revenue_rows(rows, request)
    n = request.get('window')
    if n not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
