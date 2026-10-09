"""Pure-Python transformations for row-oriented sales data."""
from statistics import mean, median


def _filled(rows, request):
    out = [dict(r) for r in rows]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode not in ('zero', 'mean', 'median'):
        raise ValueError("fill must be zero, mean, or median")
    fill = 0 if mode == 'zero' or not vals else mean(vals) if mode == 'mean' else median(vals)
    for r in out:
        if r.get('units') is None: r['units'] = fill
        region = r.get('region')
        r['region'] = region.strip().lower() if region is not None else None
    return out


def clean(rows, lookup, request):
    return _filled(rows, request)


def revenue(rows, lookup, request):
    out = _filled(rows, request)
    for r in out:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def _agg(vals, agg):
    vals = [v for v in vals if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return mean(vals) if vals else None
    raise ValueError("agg must be sum, mean, or count")


def group(rows, lookup, request):
    buckets = {}
    for r in revenue(rows, lookup, request):
        k = r.get('region')
        if k is not None: buckets.setdefault(k, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': k, agg+'_revenue_cents': _agg(v, agg)} for k,v in sorted(buckets.items(), key=lambda x: str(x[0]))]


def monthly(rows, lookup, request):
    buckets = {}
    for r in revenue(rows, lookup, request):
        d, reg = r.get('date'), r.get('region')
        m = d[:7] if d is not None else None
        if m is not None and reg is not None: buckets.setdefault((m,reg), []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'month':m,'region':r,agg+'_revenue_cents':_agg(buckets[(m,r)],agg)} for m,r in sorted(buckets,key=lambda x:(str(x[0]),str(x[1])))]


def lookup(rows, lookup, request):
    out = revenue(rows, lookup, request)
    targets = {x.get('region'): x.get('target') for x in lookup}
    for r in out:
        t, v = targets.get(r.get('region')), r['revenue_cents']
        r['revenue_cents_per_target'] = v/t if v is not None and t not in (None,0) else None
    return out


def window(rows, lookup, request):
    out = revenue(rows, lookup, request)
    width = request.get('window', 2)
    if width not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0,i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = mean(vals) if vals else None
    return out

CHECKS = {name: globals()[name] for name in ('clean','revenue','group','monthly','lookup','window')}
