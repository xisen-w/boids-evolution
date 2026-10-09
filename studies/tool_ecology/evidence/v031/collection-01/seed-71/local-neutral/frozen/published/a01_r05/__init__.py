"""Native row-oriented sales transformations."""
from statistics import mean, median


def _fill(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = {'zero': 0, 'mean': (mean(vals) if vals else 0), 'median': (median(vals) if vals else 0)}.get(mode)
    if mode not in ('zero', 'mean', 'median'):
        raise ValueError("fill must be zero, mean, or median")
    return [dict(r, units=(replacement if r.get('units') is None else r.get('units'))) for r in rows]


def _normalized(rows, request):
    out = _fill(rows, request.get('fill', 'zero'))
    for r in out:
        region = r.get('region')
        r['region'] = region.strip().lower() if isinstance(region, str) else region
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    out = _fill(rows, request.get('fill', 'zero'))
    for r in out:
        v = r.get('region')
        r['region'] = v.strip().lower() if isinstance(v, str) else v
    return out


def revenue(rows, lookup, request):
    return _normalized(rows, request)


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals) / len(vals) if vals else None
    raise ValueError('agg must be sum, mean, or count')


def _groups(data, keys, agg):
    groups = {}
    for r in data:
        key = tuple(r.get(k) for k in keys)
        if any(x is None for x in key): continue
        groups.setdefault(key, []).append(r.get('revenue_cents'))
    out = []
    for key in sorted(groups, key=lambda t: tuple(str(x) for x in t)):
        row = dict(zip(keys, key)); row[agg + '_revenue_cents'] = _aggregate(groups[key], agg); out.append(row)
    return out


def group(rows, lookup, request):
    agg = request.get('agg', 'sum')
    return _groups(_normalized(rows, request), ['region'], agg)


def monthly(rows, lookup, request):
    data = _normalized(rows, request)
    for r in data:
        d = r.get('date'); r['month'] = d[:7] if d is not None else None
    return _groups(data, ['month', 'region'], request.get('agg', 'sum'))


def lookup(rows, lookup, request):
    data = _normalized(rows, request)
    targets = {}
    for item in lookup:
        reg = item.get('region'); reg = reg.strip().lower() if isinstance(reg, str) else reg
        targets[reg] = item.get('target')
    for r in data:
        target = targets.get(r.get('region'))
        r['revenue_cents_per_target'] = (r['revenue_cents'] / target if r['revenue_cents'] is not None and target not in (None, 0) else None)
    return data


def window(rows, lookup, request):
    data = _normalized(rows, request)
    n = request.get('window', 2)
    if n not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(data):
        vals = [x['revenue_cents'] for x in data[max(0, i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return data
