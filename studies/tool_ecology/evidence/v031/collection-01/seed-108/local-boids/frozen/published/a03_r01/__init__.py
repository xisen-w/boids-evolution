"""Small, dependency-free implementations of the recurring row-table services."""
from statistics import median

_MISSING = object()

def _fill(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if method == 'zero' or not vals:
        value = 0
    elif method == 'mean':
        value = sum(vals) / len(vals)
    elif method == 'median':
        value = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [value if r.get('units') is None else r.get('units') for r in rows]

def _region(value):
    return value.strip().lower() if isinstance(value, str) else value

def _base(rows, request):
    units = _fill(rows, request.get('fill', 'zero'))
    out=[]
    for r,u in zip(rows, units):
        x=dict(r)
        x['region'] = _region(r.get('region'))
        x['units'] = u
        x['revenue_cents'] = None if u is None or r.get('price_cents') is None else u*r['price_cents']
        out.append(x)
    return out

def clean(rows, lookup, request):
    units = _fill(rows, request.get('fill', 'zero'))
    return [dict(r, region=_region(r.get('region')), units=u) for r,u in zip(rows, units)]

def revenue(rows, lookup, request):
    return _base(rows, request)

def _aggregate(vals, agg):
    good=[v for v in vals if v is not None]
    if agg == 'sum': return sum(good)
    if agg == 'count': return len(good)
    if agg == 'mean': return sum(good)/len(good) if good else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")

def _group(rows, request, monthly=False):
    data=_base(rows, request)
    buckets={}
    for r in data:
        region=r.get('region')
        month=(r.get('date')[:7] if r.get('date') is not None else None) if monthly else None
        if region is None or (monthly and month is None): continue
        key=(month, region) if monthly else (region,)
        buckets.setdefault(key, []).append(r['revenue_cents'])
    agg=request.get('agg','sum')
    keys=sorted(buckets, key=lambda k: tuple(str(x) for x in k))
    result=[]
    for key in keys:
        row={}
        if monthly: row['month']=key[0]
        row['region']=key[-1]
        row[agg+'_revenue_cents']=_aggregate(buckets[key],agg)
        result.append(row)
    return result

def group(rows, lookup, request):
    return _group(rows, request)

def monthly(rows, lookup, request):
    return _group(rows, request, True)

def lookup(rows, lookup, request):
    data=_base(rows, request)
    targets={r.get('region'):r.get('target') for r in lookup}
    for r in data:
        target=targets.get(r.get('region'))
        val=r['revenue_cents']
        r['revenue_cents_per_target'] = None if target is None or target == 0 or val is None else val/target
    return data

def window(rows, lookup, request):
    data=_base(rows, request)
    n=request.get('window', 2)
    if not isinstance(n,int) or n <= 0: raise ValueError('window must be a positive integer')
    for i,r in enumerate(data):
        vals=[x['revenue_cents'] for x in data[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return data
