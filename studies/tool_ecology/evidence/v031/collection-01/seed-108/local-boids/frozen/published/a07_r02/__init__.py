"""Reusable table transforms for the six publication service families."""
from statistics import mean, median

_MISSING = object()

def _region(value):
    return value.strip().lower() if isinstance(value, str) else value

def _filled(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if method == 'zero' or not vals:
        replacement = 0
    elif method == 'mean':
        replacement = mean(vals)
    elif method == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [replacement if r.get('units') is None else r.get('units') for r in rows]

def clean(rows, request):
    units = _filled(rows, request.get('fill', 'zero'))
    result=[]
    for r,u in zip(rows, units):
        x=dict(r); x['region']=_region(r.get('region')); x['units']=u; result.append(x)
    return result

def _derived(rows, request):
    units = _filled(rows, request.get('fill', 'zero'))
    out=[]
    for r, u in zip(rows, units):
        x=dict(r)
        x['units'] = u
        p=r.get('price_cents')
        x['revenue_cents'] = None if u is None or p is None else u*p
        out.append(x)
    return out

def revenue(rows, lookup, request):
    return _derived(rows, request)

def _aggregate(values, agg):
    vals=[v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")

def _groups(rows, request, monthly=False):
    derived=_derived(rows,request); buckets={}
    for r in derived:
        region=_region(r.get('region')); month=(r.get('date')[:7] if r.get('date') is not None else None) if monthly else None
        if region is None or (monthly and month is None): continue
        key=(month,region) if monthly else (region,)
        buckets.setdefault(key,[]).append(r['revenue_cents'])
    agg=request.get('agg','sum'); suffix=f'{agg}_revenue_cents'
    keys=sorted(buckets, key=lambda k: tuple(str(v) for v in k))
    result=[]
    for key in keys:
        item=({'month':key[0],'region':key[1]} if monthly else {'region':key[0]})
        item[suffix]=_aggregate(buckets[key],agg); result.append(item)
    return result

def group(rows, lookup, request):
    return _groups(rows,request)

def monthly(rows, lookup, request):
    return _groups(rows,request,True)

def lookup(rows, lookup, request):
    out=_derived(rows,request)
    targets={_region(x.get('region')):x.get('target') for x in lookup}
    for x in out:
        x['region'] = _region(x.get('region'))
        target=targets.get(x.get('region')); value=x['revenue_cents']
        x['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value/target
    return out

def window(rows, lookup, request):
    out=_derived(rows,request); n=request.get('window')
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,x in enumerate(out):
        vals=[r['revenue_cents'] for r in out[max(0,i-n+1):i+1] if r['revenue_cents'] is not None]
        x['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out

# Stable service adapters; clean is independent of lookup.
def clean_service(rows, lookup, request): return clean(rows,request)
def revenue_service(rows, lookup, request): return revenue(rows,lookup,request)
def group_service(rows, lookup, request): return group(rows,lookup,request)
def monthly_service(rows, lookup, request): return monthly(rows,lookup,request)
def lookup_service(rows, lookup, request): return globals()['lookup'](rows,lookup,request)
def window_service(rows, lookup, request): return window(rows,lookup,request)
