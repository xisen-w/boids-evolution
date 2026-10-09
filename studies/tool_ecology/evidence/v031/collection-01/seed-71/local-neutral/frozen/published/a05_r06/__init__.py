"""Pure-Python row-table transformations for the six service families."""
from statistics import median


def _filled(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if not vals:
        replacement = 0
    elif mode == 'mean':
        replacement = sum(vals) / len(vals)
    elif mode == 'median':
        replacement = median(vals)
    else:
        replacement = 0
    return [dict(r, units=(replacement if r.get('units') is None else r.get('units'))) for r in rows]


def _normalized(rows, request):
    out = _filled(rows, request)
    for r in out:
        region = r.get('region')
        r['region'] = region.strip().lower() if isinstance(region, str) else region
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    return [{**r, 'region': (r.get('region').strip().lower() if isinstance(r.get('region'), str) else r.get('region')),
             'units': u} for r, u in zip(rows, [x['units'] for x in _filled(rows, request)])]


def revenue(rows, lookup, request):
    return _normalized(rows, request)


def _aggregate(vals, agg):
    vals = [v for v in vals if v is not None]
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals) / len(vals) if vals else None
    return sum(vals)


def group(rows, lookup, request):
    agg = request.get('agg', 'sum')
    buckets = {}
    for r in _normalized(rows, request):
        key = r['region']
        if key is not None: buckets.setdefault(key, []).append(r['revenue_cents'])
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(v, agg)}
            for k, v in sorted(buckets.items(), key=lambda item: str(item[0]))]


def monthly(rows, lookup, request):
    agg = request.get('agg', 'sum')
    buckets = {}
    for r in _normalized(rows, request):
        date = r.get('date')
        month = date[:7] if date is not None else None
        key = (month, r['region'])
        if None not in key: buckets.setdefault(key, []).append(r['revenue_cents'])
    return [{'month': k[0], 'region': k[1], f'{agg}_revenue_cents': _aggregate(v, agg)}
            for k, v in sorted(buckets.items(), key=lambda item: tuple(str(x) for x in item[0]))]


def lookup(rows, lookup, request):
    out = _normalized(rows, request)
    targets = {r.get('region'): r.get('target') for r in lookup if r.get('region') is not None}
    for r in out:
        target = targets.get(r.get('region'))
        value = r['revenue_cents']
        r['revenue_cents_per_target'] = None if target in (None, 0) or value is None else value / target
    return out


def window(rows, lookup, request):
    out = _normalized(rows, request)
    width = request.get('window', 2)
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
