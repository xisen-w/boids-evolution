"""Pure-Python table transformations for the six publication service families."""
from collections import defaultdict

_MISSING = object()

def _fill_units(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if not vals: replacement = 0
    elif mode == 'zero': replacement = 0
    elif mode == 'mean': replacement = sum(vals) / len(vals)
    elif mode == 'median':
        s = sorted(vals); n = len(s)
        replacement = s[n//2] if n % 2 else (s[n//2-1] + s[n//2]) / 2
    else: raise ValueError("fill must be zero, mean, or median")
    return [dict(r, units=(replacement if r.get('units') is None else r.get('units'))) for r in rows]

def _region(v): return v.strip().lower() if isinstance(v, str) else v

def clean(rows, lookup, request):
    return [dict(r, region=_region(r.get('region'))) for r in _fill_units(rows, request.get('fill'))]

def _revenue_rows(rows, request):
    out=[]
    for r in _fill_units(rows, request.get('fill')):
        v=dict(r); u=v.get('units'); p=v.get('price_cents')
        v['revenue_cents'] = None if u is None or p is None else u*p
        out.append(v)
    return out

def revenue(rows, lookup, request): return _revenue_rows(rows, request)

def _aggregate(values, agg):
    vals=[v for v in values if v is not None]
    if agg=='sum': return sum(vals)
    if agg=='count': return len(vals)
    if agg=='mean': return sum(vals)/len(vals) if vals else None
    raise ValueError('agg must be sum, mean, or count')

def group(rows, lookup, request):
    buckets=defaultdict(list)
    for r in _revenue_rows(rows, request):
        key=_region(r.get('region'))
        if key is not None: buckets[key].append(r['revenue_cents'])
    agg=request.get('agg')
    return [{'region':k, agg+'_revenue_cents':_aggregate(v,agg)} for k,v in sorted(buckets.items(),key=lambda x:str(x[0]))]

def monthly(rows, lookup, request):
    buckets=defaultdict(list)
    for r in _revenue_rows(rows,request):
        key=_region(r.get('region')); date=r.get('date'); month=date[:7] if date is not None else None
        if key is not None and month is not None: buckets[(month,key)].append(r['revenue_cents'])
    agg=request.get('agg')
    return [{'month':m,'region':r,agg+'_revenue_cents':_aggregate(v,agg)} for (m,r),v in sorted(buckets.items(),key=lambda x:(str(x[0][0]),str(x[0][1])))]

def lookup(rows, lookup, request):
    targets={_region(r.get('region')):r.get('target') for r in lookup}
    out=[]
    for r in _revenue_rows(rows,request):
        v=dict(r); region=_region(v.get('region')); target=targets.get(region); rev=v['revenue_cents']
        v['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev/target
        out.append(v)
    return out

def window(rows, lookup, request):
    result=_revenue_rows(rows,request); width=request.get('window')
    if width not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    vals=[]
    for i,r in enumerate(result):
        vals.append(r['revenue_cents']); recent=[x for x in vals[max(0,i-width+1):i+1] if x is not None]
        r['roll_revenue_cents']=sum(recent)/len(recent) if recent else None
    return result
