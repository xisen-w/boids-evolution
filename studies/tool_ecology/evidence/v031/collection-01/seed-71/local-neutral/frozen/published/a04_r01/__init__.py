"""Native implementations of the tabular service families."""
from statistics import median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _filled(rows, fill):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero': v = 0
    elif not vals: v = 0
    elif fill == 'mean': v = sum(vals) / len(vals)
    elif fill == 'median': v = median(vals)
    else: raise ValueError("fill must be zero, mean, or median")
    return [dict(r, units=(v if r.get('units') is None else r.get('units'))) for r in rows]


def clean(rows, lookup, request):
    out = _filled(rows, request['fill'])
    for r in out: r['region'] = _region(r.get('region'))
    return out


def _revenue_rows(rows, request):
    out = _filled(rows, request['fill'])
    for r in out:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def revenue(rows, lookup, request):
    return _revenue_rows(rows, request)


def _aggregate(vals, agg):
    values = [v for v in vals if v is not None]
    if agg == 'sum': return sum(values)
    if agg == 'count': return len(values)
    if agg == 'mean': return sum(values) / len(values) if values else None
    raise ValueError("agg must be sum, mean, or count")


def group(rows, lookup, request):
    data = _revenue_rows(rows, request)
    groups = {}
    for r in data:
        key = _region(r.get('region'))
        if key is not None: groups.setdefault(key, []).append(r.get('revenue_cents'))
    agg = request['agg']
    return [{'region': k, agg + '_revenue_cents': _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    data = _revenue_rows(rows, request)
    groups = {}
    for r in data:
        region = _region(r.get('region'))
        date = r.get('date')
        month = date[:7] if date is not None else None
        if region is not None and month is not None:
            groups.setdefault((month, region), []).append(r.get('revenue_cents'))
    agg = request['agg']
    return [{'month': m, 'region': r, agg + '_revenue_cents': _aggregate(groups[(m,r)], agg)}
            for m,r in sorted(groups, key=lambda x: (str(x[0]), str(x[1])))]


def lookup(rows, lookup, request):
    data = _revenue_rows(rows, request)
    targets = {}
    for item in lookup:
        targets[_region(item.get('region'))] = item.get('target')
    for r in data:
        target = targets.get(_region(r.get('region')))
        rev = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return data


def window(rows, lookup, request):
    data = _revenue_rows(rows, request)
    n = request['window']
    if n not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(data):
        vals = [x.get('revenue_cents') for x in data[max(0, i-n+1):i+1] if x.get('revenue_cents') is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return data
