"""Pure-Python row table analytics."""
from statistics import mean, median

_MISSING = object()

def _option(request, key, default):
    return request.get(key, default) if request is not None else default

def _filled(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = _option(request, 'fill', 'zero')
    if mode == 'zero' or not vals: fill = 0
    elif mode == 'mean': fill = mean(vals)
    elif mode == 'median': fill = median(vals)
    else: raise ValueError("fill must be zero, mean, or median")
    return [dict(r, units=fill if r.get('units') is None else r.get('units')) for r in rows]

def _region(row):
    v = row.get('region')
    return v.strip().lower() if isinstance(v, str) else v

def clean(rows, lookup, request):
    return [dict(r, region=_region(r), units=u['units']) for r,u in zip(rows,_filled(rows, request))]

def _derived(rows, request):
    out = _filled(rows, request)
    for r in out:
        r['region'] = _region(r)
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u*p
    return out

def revenue(rows, lookup, request): return _derived(rows, request)

def _aggregate(vals, agg):
    vals = [v for v in vals if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return mean(vals) if vals else None
    raise ValueError('agg must be sum, mean, or count')

def _groups(rows, request, monthly_mode):
    agg = _option(request, 'agg', 'sum')
    if agg not in ('sum','mean','count'): raise ValueError('agg must be sum, mean, or count')
    buckets = {}
    for r in _derived(rows, request):
        region = r.get('region'); month = (str(r.get('date'))[:7] if r.get('date') is not None else None)
        key = (month, region) if monthly_mode else (region,)
        if any(k is None for k in key): continue
        buckets.setdefault(key, []).append(r.get('revenue_cents'))
    def sortkey(k): return tuple(str(x) for x in k)
    out=[]
    for key in sorted(buckets, key=sortkey):
        d = ({'month':key[0], 'region':key[1]} if monthly_mode else {'region':key[0]})
        d[agg+'_revenue_cents'] = _aggregate(buckets[key], agg)
        out.append(d)
    return out

def group(rows, lookup, request): return _groups(rows, request, False)
def monthly(rows, lookup, request): return _groups(rows, request, True)

def lookup(rows, lookup, request):
    targets = {}
    for item in lookup:
        key = _region(item)
        targets[key] = item.get('target')
    out = _derived(rows, request)
    for r in out:
        target = targets.get(r.get('region'))
        rev = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev/target
    return out

def window(rows, lookup, request):
    out = _derived(rows, request)
    width = _option(request, 'window', 2)
    if not isinstance(width, int) or width <= 0: raise ValueError('window must be positive integer')
    for i,r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0,i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = mean(vals) if vals else None
    return out
