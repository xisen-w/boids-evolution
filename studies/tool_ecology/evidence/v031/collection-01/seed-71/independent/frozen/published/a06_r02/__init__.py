"""Native implementations of the six tabular service families."""
from statistics import mean, median


def _fill(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero': v = 0
    elif not vals: v = 0
    elif mode == 'mean': v = mean(vals)
    elif mode == 'median': v = median(vals)
    else: raise ValueError("fill must be zero, mean, or median")
    return [dict(r, units=(r.get('units') if r.get('units') is not None else v)) for r in rows]


def _base(rows, request, normalize=True):
    out = _fill(rows, request.get('fill', 'zero'))
    for r in out:
        if normalize:
            r['region'] = r.get('region').strip().lower() if isinstance(r.get('region'), str) else r.get('region')
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    out = _fill(rows, request.get('fill', 'zero'))
    for r in out:
        r['region'] = r.get('region').strip().lower() if isinstance(r.get('region'), str) else r.get('region')
    return out


def revenue(rows, lookup, request):
    return _base(rows, request, normalize=False)


def _aggregate(vals, agg):
    vals = [v for v in vals if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals) / len(vals) if vals else None
    raise ValueError('agg must be sum, mean, or count')


def group(rows, lookup, request):
    buckets = {}
    for r in _base(rows, request):
        key = r.get('region')
        if key is not None: buckets.setdefault(key, []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'region': k, agg+'_revenue_cents': _aggregate(buckets[k], agg)} for k in sorted(buckets, key=str)]


def monthly(rows, lookup, request):
    buckets = {}
    for r in _base(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            buckets.setdefault((month, region), []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': reg, agg+'_revenue_cents': _aggregate(buckets[(m, reg)], agg)}
            for m, reg in sorted(buckets, key=lambda x: (str(x[0]), str(x[1])))]


def lookup(rows, lookup, request):
    out = _base(rows, request)
    targets = {}
    for item in lookup:
        region = item.get('region')
        if isinstance(region, str): region = region.strip().lower()
        targets[region] = item.get('target')
    for r in out:
        target = targets.get(r.get('region'))
        rev = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return out


def window(rows, lookup, request):
    out = _base(rows, request, normalize=False)
    n = request.get('window', 2)
    if not isinstance(n, int) or n <= 0: raise ValueError('window must be a positive integer')
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
