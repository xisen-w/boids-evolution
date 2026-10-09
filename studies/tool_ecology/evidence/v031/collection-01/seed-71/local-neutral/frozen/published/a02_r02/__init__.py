"""Dependency-free tabular service functions."""
from collections import defaultdict

def _units(rows, request):
    vals=[r.get('units') for r in rows if r.get('units') is not None]
    mode=request.get('fill','zero')
    if not vals: fill=0
    elif mode=='zero': fill=0
    elif mode=='mean': fill=sum(vals)/len(vals)
    elif mode=='median':
        s=sorted(vals); n=len(s); fill=s[n//2] if n%2 else (s[n//2-1]+s[n//2])/2
    else: raise ValueError('fill must be zero, mean, or median')
    return [r.get('units') if r.get('units') is not None else fill for r in rows]

def _region(v): return v.strip().lower() if isinstance(v,str) else None

def _revenue_rows(rows, request, normalize=False):
    result=[]
    for r,u in zip(rows,_units(rows,request)):
        o=dict(r); o['units']=u
        if normalize: o['region']=_region(r.get('region'))
        p=r.get('price_cents'); o['revenue_cents']=None if p is None or u is None else u*p
        result.append(o)
    return result

def clean(rows, lookup, request):
    return [dict(r, region=_region(r.get('region')), units=u) for r,u in zip(rows,_units(rows,request))]

def revenue(rows, lookup, request): return _revenue_rows(rows,request)

def _agg(v, kind):
    if kind=='sum': return sum(v) if v else 0
    if kind=='count': return len(v)
    if kind=='mean': return sum(v)/len(v) if v else None
    raise ValueError('agg must be sum, mean, or count')

def group(rows, lookup, request):
    b=defaultdict(list)
    for r in _revenue_rows(rows,request,True):
        k=r.get('region')
        if k is not None:
            b[k]
            if r['revenue_cents'] is not None: b[k].append(r['revenue_cents'])
    a=request.get('agg','sum')
    return [{'region':k,a+'_revenue_cents':_agg(b[k],a)} for k in sorted(b,key=str)]

def monthly(rows, lookup, request):
    b=defaultdict(list)
    for r in _revenue_rows(rows,request,True):
        d=r.get('date'); m=d[:7] if d is not None else None; k=r.get('region')
        if m is None or k is None: continue
        b[(m,k)]
        if r['revenue_cents'] is not None: b[(m,k)].append(r['revenue_cents'])
    a=request.get('agg','sum')
    return [{'month':m,'region':k,a+'_revenue_cents':_agg(b[(m,k)],a)} for m,k in sorted(b,key=lambda x:(str(x[0]),str(x[1])))]

def lookup(rows, lookup, request):
    targets={_region(x.get('region')):x.get('target') for x in lookup}
    out=_revenue_rows(rows,request,True)
    for r in out:
        t=targets.get(r.get('region')); v=r['revenue_cents']
        r['revenue_cents_per_target']=None if t is None or t==0 or v is None else v/t
    return out

def window(rows, lookup, request):
    out=_revenue_rows(rows,request)
    n=request.get('window',2)
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        v=[x['revenue_cents'] for x in out[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(v)/len(v) if v else None
    return out
