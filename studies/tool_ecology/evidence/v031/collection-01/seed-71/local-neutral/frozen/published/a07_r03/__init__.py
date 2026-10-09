"""Small dependency-free table transforms for the six recurring services."""
from statistics import mean, median

_MISSING = object()

def _filled(rows, request):
    vals=[r.get('units') for r in rows if r.get('units') is not None]
    mode=request.get('fill','zero')
    if mode=='mean': replacement=mean(vals) if vals else 0
    elif mode=='median': replacement=median(vals) if vals else 0
    else: replacement=0
    out=[]
    for r in rows:
        d=dict(r)
        if d.get('units') is None: d['units']=replacement
        yield d

def _base(rows, request):
    out=[]
    for d in _filled(rows,request):
        d['region']=d.get('region').strip().lower() if isinstance(d.get('region'),str) else d.get('region')
        u,p=d.get('units'),d.get('price_cents')
        d['revenue_cents']=u*p if u is not None and p is not None else None
        out.append(d)
    return out

def clean(rows, lookup, request):
    return [dict(d, region=d.get('region').strip().lower() if isinstance(d.get('region'),str) else d.get('region')) for d in _filled(rows,request)]

def revenue(rows, lookup, request): return _base(rows,request)

def _aggregate(vals, agg):
    vals=[v for v in vals if v is not None]
    if agg=='count': return len(vals)
    if agg=='mean': return sum(vals)/len(vals) if vals else None
    return sum(vals)

def _groups(rows, request, monthly=False):
    agg=request.get('agg','sum'); buckets={}
    for r in _base(rows,request):
        region=r.get('region'); month=(r.get('date')[:7] if r.get('date') is not None else None)
        key=(month,region) if monthly else (region,)
        if any(x is None for x in key): continue
        buckets.setdefault(key,[]).append(r.get('revenue_cents'))
    def sk(k): return tuple(str(x) for x in k)
    result=[]
    for key in sorted(buckets,key=sk):
        v=_aggregate(buckets[key],agg)
        d=({'month':key[0],'region':key[1]} if monthly else {'region':key[0]})
        d[agg+'_revenue_cents']=v
        result.append(d)
    return result

def group(rows, lookup, request): return _groups(rows,request)
def monthly(rows, lookup, request): return _groups(rows,request,True)

def lookup(rows, lookup, request):
    targets={(x.get('region').strip().lower() if isinstance(x.get('region'),str) else x.get('region')):x.get('target') for x in lookup}
    out=[]
    for d in _base(rows,request):
        t=targets.get(d.get('region')); rev=d['revenue_cents']
        d['revenue_cents_per_target']=rev/t if rev is not None and t not in (None,0) else None
        out.append(d)
    return out

def window(rows, lookup, request):
    out=_base(rows,request); n=request.get('window',2); history=[]
    for d in out:
        history.append(d.get('revenue_cents'))
        vals=[v for v in history[-n:] if v is not None]
        d['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out
