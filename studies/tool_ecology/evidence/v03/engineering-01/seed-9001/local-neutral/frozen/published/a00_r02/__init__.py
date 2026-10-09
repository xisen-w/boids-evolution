"""Dependency-free services over lists of row dictionaries."""
from statistics import mean, median

def _fill(rows, req):
    vals=[r.get('units') for r in rows if r.get('units') is not None]
    mode=req.get('fill','zero')
    if mode not in ('zero','mean','median'): raise ValueError('fill must be zero, mean, or median')
    replacement=0 if not vals or mode=='zero' else mean(vals) if mode=='mean' else median(vals)
    return [replacement if r.get('units') is None else r.get('units') for r in rows]

def _copy(rows, normalized=False):
    out=[dict(r) for r in rows]
    if normalized:
        for r in out:
            v=r.get('region'); r['region']=v.strip().lower() if isinstance(v,str) else v
    return out

def clean(rows, lookup, request):
    out=_copy(rows,True)
    for r,u in zip(out,_fill(rows,request)): r['units']=u
    return out

def revenue(rows, lookup, request):
    out=_copy(rows)
    for r,u in zip(out,_fill(rows,request)):
        r['units']=u; r['revenue_cents']=None if u is None or r.get('price_cents') is None else u*r['price_cents']
    return out

def _base(rows, lookup, request): return clean(rows,lookup,request) if False else revenue(rows,lookup,request)
def _agg(vals, kind):
    vals=[v for v in vals if v is not None]
    if kind=='sum': return sum(vals)
    if kind=='count': return len(vals)
    if kind=='mean': return sum(vals)/len(vals) if vals else None
    raise ValueError('agg must be sum, mean, or count')
def _normalized_revenue(rows,lookup,request):
    out=revenue(rows,lookup,request)
    for r in out:
        v=r.get('region'); r['region']=v.strip().lower() if isinstance(v,str) else v
    return out
def group(rows,lookup,request):
    g={}; kind=request.get('agg','sum')
    for r in _normalized_revenue(rows,lookup,request):
        k=r.get('region')
        if k is not None:g.setdefault(k,[]).append(r.get('revenue_cents'))
    return [{'region':k,kind+'_revenue_cents':_agg(g[k],kind)} for k in sorted(g,key=str)]
def monthly(rows,lookup,request):
    g={}; kind=request.get('agg','sum')
    for r in _normalized_revenue(rows,lookup,request):
        d=r.get('date'); m=d[:7] if d is not None else None; k=r.get('region')
        if m is not None and k is not None:g.setdefault((m,k),[]).append(r.get('revenue_cents'))
    return [{'month':m,'region':r,kind+'_revenue_cents':_agg(g[(m,r)],kind)} for m,r in sorted(g,key=lambda x:(str(x[0]),str(x[1])))]
def lookup(rows, lookup, request):
    targets={}
    for x in lookup:
        k=x.get('region'); k=k.strip().lower() if isinstance(k,str) else k; targets[k]=x.get('target')
    out=_normalized_revenue(rows,lookup,request)
    for r in out:
        t=targets.get(r.get('region')); v=r.get('revenue_cents')
        r['revenue_cents_per_target']=None if t is None or t==0 or v is None else v/t
    return out
def window(rows,lookup,request):
    out=revenue(rows,lookup,request); n=request.get('window',2)
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        v=[x['revenue_cents'] for x in out[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(v)/len(v) if v else None
    return out
serve_clean=clean
serve_revenue=revenue
serve_group=group
serve_monthly=monthly
serve_lookup=lookup
serve_window=window
