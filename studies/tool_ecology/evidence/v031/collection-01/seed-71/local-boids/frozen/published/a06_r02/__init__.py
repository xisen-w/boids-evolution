"""Pure-Python row table service adapters."""
from statistics import median

def _fill(rows, request):
    mode=request.get('fill','zero')
    vals=[r.get('units') for r in rows if r.get('units') is not None]
    if mode=='zero' or not vals: x=0
    elif mode=='mean': x=sum(vals)/len(vals)
    elif mode=='median': x=median(vals)
    else: raise ValueError('fill must be zero, mean, or median')
    return [x if r.get('units') is None else r.get('units') for r in rows]

def _base(rows, request, normalize=False):
    units=_fill(rows,request); out=[]
    for row,u in zip(rows,units):
        r=dict(row); r['units']=u
        if normalize and isinstance(r.get('region'),str): r['region']=r['region'].strip().lower()
        out.append(r)
    return out

def _rev(rows,request,normalize=False):
    out=_base(rows,request,normalize)
    for r in out:
        p=r.get('price_cents'); u=r.get('units')
        r['revenue_cents']=None if p is None or u is None else u*p
    return out

def clean(rows,lookup,request): return _base(rows,request,True)
def revenue(rows,lookup,request): return _rev(rows,request)
def _agg(v,a):
    v=[x for x in v if x is not None]
    if a=='sum': return sum(v)
    if a=='count': return len(v)
    if a=='mean': return sum(v)/len(v) if v else None
    raise ValueError('agg must be sum, mean, or count')
def group(rows,lookup,request):
    g={}
    for r in _rev(rows,request,True):
        k=r.get('region')
        if k is not None: g.setdefault(k,[]).append(r['revenue_cents'])
    a=request.get('agg','sum')
    return [{'region':k,a+'_revenue_cents':_agg(g[k],a)} for k in sorted(g,key=str)]
def monthly(rows,lookup,request):
    g={}
    for r in _rev(rows,request,True):
        m=r.get('date'); m=m[:7] if m is not None else None; k=r.get('region')
        if m is not None and k is not None: g.setdefault((m,k),[]).append(r['revenue_cents'])
    a=request.get('agg','sum')
    return [{'month':m,'region':k,a+'_revenue_cents':_agg(g[(m,k)],a)} for m,k in sorted(g,key=lambda x:(str(x[0]),str(x[1])))]
def lookup(rows,lookup,request):
    targets={}
    for x in lookup:
        k=x.get('region'); k=k.strip().lower() if isinstance(k,str) else k
        targets[k]=x.get('target')
    out=_rev(rows,request,True)
    for r in out:
        t=targets.get(r.get('region')); v=r['revenue_cents']
        r['revenue_cents_per_target']=None if t is None or t==0 or v is None else v/t
    return out
def window(rows,lookup,request):
    out=_rev(rows,request); w=request.get('window')
    if w not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-w+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out
