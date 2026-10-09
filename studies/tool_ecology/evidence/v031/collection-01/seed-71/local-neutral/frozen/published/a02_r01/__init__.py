"""Reusable implementations of the six tabular service families."""
from collections import defaultdict


def _region(value):
    return value.strip().lower() if isinstance(value, str) else None


def _filled_units(rows, request):
    values = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if not values:
        fill = 0
    elif mode == 'zero':
        fill = 0
    elif mode == 'mean':
        fill = sum(values) / len(values)
    elif mode == 'median':
        v = sorted(values); n = len(v)
        fill = v[n // 2] if n % 2 else (v[n//2-1] + v[n//2]) / 2
    else:
        raise ValueError("fill must be zero, mean, or median")
    return [fill if r.get('units') is None else r.get('units') for r in rows]


def _base(rows, request):
    units = _filled_units(rows, request)
    result = []
    for row, u in zip(rows, units):
        out = dict(row)
        out['region'] = _region(row.get('region'))
        out['units'] = u
        p = row.get('price_cents')
        out['revenue_cents'] = None if u is None or p is None else u * p
        result.append(out)
    return result


def clean(rows, lookup, request):
    units = _filled_units(rows, request)
    return [dict(r, region=_region(r.get('region')), units=u) for r, u in zip(rows, units)]


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(items, agg):
    if agg == 'sum': return sum(items) if items else 0
    if agg == 'count': return len(items)
    if agg == 'mean': return sum(items) / len(items) if items else None
    raise ValueError("agg must be sum, mean, or count")


def group(rows, lookup, request):
    buckets = defaultdict(list)
    for row in _base(rows, request):
        if row['region'] is not None and row['revenue_cents'] is not None:
            buckets[row['region']].append(row['revenue_cents'])
        elif row['region'] is not None:
            buckets.setdefault(row['region'], [])
    agg = request.get('agg', 'sum')
    return [{'region': k, agg+'_revenue_cents': _aggregate(v, agg)} for k, v in sorted(buckets.items(), key=lambda x: str(x[0]))]


def monthly(rows, lookup, request):
    buckets = defaultdict(list)
    for row in _base(rows, request):
        date = row.get('date')
        month = date[:7] if date is not None else None
        region = row['region']
        if month is None or region is None: continue
        buckets[(month, region)].append(row['revenue_cents']) if row['revenue_cents'] is not None else buckets.setdefault((month, region), [])
    agg = request.get('agg', 'sum')
    keys = sorted(buckets, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': r, agg+'_revenue_cents': _aggregate(buckets[(m,r)], agg)} for m,r in keys]


def lookup(rows, lookup, request):
    targets = {}
    for item in lookup:
        targets[_region(item.get('region'))] = item.get('target')
    out = _base(rows, request)
    for row in out:
        target = targets.get(row['region'])
        revenue_value = row['revenue_cents']
        row['revenue_cents_per_target'] = None if target is None or target == 0 or revenue_value is None else revenue_value / target
    return out


def window(rows, lookup, request):
    out = _base(rows, request)
    n = request.get('window', 2)
    if n not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, row in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-n+1):i+1] if x['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(vals)/len(vals) if vals else None
    return out
