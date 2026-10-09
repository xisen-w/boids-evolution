"""Native implementations of the recurring table services."""
from statistics import mean, median

_MISSING = object()

def _region(x):
    return x.strip().lower() if isinstance(x, str) else x

def _filled(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = 0 if not vals else (0 if mode == 'zero' else mean(vals) if mode == 'mean' else median(vals))
    out=[]
    for row in rows:
        r=dict(row)
        if r.get('units') is None: r['units']=replacement
        out.append(r)
    return out

def _revenue(rows, request):
    out=_filled(rows, request.get('fill', 'zero'))
    for r in out:
        u,p=r.get('units'),r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u*p
    return out

def clean(rows, lookup, request):
    out=_filled(rows, request.get('fill','zero'))
    for r in out: r['region']=_region(r.get('region'))
    return out

def revenue(rows, lookup, request):
    return _revenue(rows,request)

def group(rows, lookup, request):
    data=_revenue(rows,request); groups={}
    for r in data:
        key=_region(r.get('region'))
        if key is not None: groups.setdefault(key,[]).append(r.get('revenue_cents'))
    return _aggregate(groups, request.get('agg','sum'), ('region',))

def monthly(rows, lookup, request):
    data=_revenue(rows,request); groups={}
    for r in data:
        region=_region(r.get('region')); date=r.get('date'); month=date[:7] if date is not None else None
        if region is not None and month is not None: groups.setdefault((month,region),[]).append(r.get('revenue_cents'))
    return _aggregate(groups,request.get('agg','sum'),('month','region'))

def _aggregate(groups, agg, keys):
    result=[]
    for key, vals in groups.items():
        valid=[v for v in vals if v is not None]
        value=(sum(valid) if agg=='sum' else len(valid) if agg=='count' else (sum(valid)/len(valid) if valid else None))
        if not valid and agg in ('sum','count'): value=0
        item={k:v for k,v in zip(keys,key if isinstance(key,tuple) else (key,))}
        item[agg+'_revenue_cents']=value; result.append(item)
    result.sort(key=lambda x: tuple(str(x[k]) for k in keys))
    return result

def lookup(rows, lookup, request):
    data=_revenue(rows,request)
    targets={_region(x.get('region')):x.get('target') for x in lookup if _region(x.get('region')) is not None}
    for r in data:
        r['region'] = _region(r.get('region'))
        target=targets.get(r.get('region')); value=r.get('revenue_cents')
        r['revenue_cents_per_target']=None if target in (None,0) or value is None else value/target
    return data

def window(rows, lookup, request):
    data=_revenue(rows,request); width=request.get('window',2)
    for i,r in enumerate(data):
        vals=[x.get('revenue_cents') for x in data[max(0,i-width+1):i+1] if x.get('revenue_cents') is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return data
