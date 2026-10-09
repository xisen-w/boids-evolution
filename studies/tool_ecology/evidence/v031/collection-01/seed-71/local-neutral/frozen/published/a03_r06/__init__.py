def _fill(rows, mode):
    vals=[r.get('units') for r in rows if r.get('units') is not None]
    if not vals: replacement=0
    elif mode=='zero': replacement=0
    elif mode=='mean': replacement=sum(vals)/len(vals)
    else:
        s=sorted(vals); n=len(s); replacement=s[n//2] if n%2 else (s[n//2-1]+s[n//2])/2
    return [replacement if r.get('units') is None else r.get('units') for r in rows]

def _base(rows, request):
    units=_fill(rows,request.get('fill'))
    out=[]
    for r,u in zip(rows,units):
        d=dict(r); d['units']=u
        region=r.get('region'); d['region']=region.strip().lower() if isinstance(region,str) else region
        a=u; b=r.get('price_cents')
        d['revenue_cents']=None if a is None or b is None else a*b
        out.append(d)
    return out

def clean(rows,lookup,request):
    u=_fill(rows,request.get('fill')); out=[]
    for r,x in zip(rows,u):
        d=dict(r); d['units']=x
        v=r.get('region'); d['region']=v.strip().lower() if isinstance(v,str) else v
        out.append(d)
    return out

def revenue(rows,lookup,request): return _base(rows,request)
def _aggregate(vals,agg):
    v=[x for x in vals if x is not None]
    if agg=='count': return len(v)
    if agg=='sum': return sum(v) if v else 0
    return sum(v)/len(v) if v else None

def _group(rows,request,monthly=False):
    data=_base(rows,request); groups={}
    for d in data:
        region=d.get('region'); month=(d.get('date')[:7] if d.get('date') is not None else None) if monthly else None
        if region is None or (monthly and month is None): continue
        key=(month,region) if monthly else (region,)
        groups.setdefault(key,[]).append(d.get('revenue_cents'))
    agg=request.get('agg')
    if agg not in ('sum','mean','count'): raise ValueError('agg must be sum, mean, or count')
    name=agg+'_revenue_cents'
    keys=sorted(groups,key=lambda k:tuple(str(x) for x in k))
    if monthly: return [{'month':k[0],'region':k[1],name:_aggregate(groups[k],agg)} for k in keys]
    return [{'region':k[0],name:_aggregate(groups[k],agg)} for k in keys]
def group(rows,lookup,request): return _group(rows,request)
def monthly(rows,lookup,request): return _group(rows,request,True)
def lookup(rows,lookup,request):
    out=_base(rows,request); targets={x.get('region'):x.get('target') for x in lookup}
    for d in out:
        vreg=d.get('region'); d['region']=vreg.strip().lower() if isinstance(vreg,str) else vreg
        t=targets.get(d.get('region')); v=d.get('revenue_cents')
        d['revenue_cents_per_target']=None if t is None or t==0 or v is None else v/t
    return out
def window(rows,lookup,request):
    out=_base(rows,request); w=request.get('window',2)
    for i,d in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-w+1):i+1] if x['revenue_cents'] is not None]
        d['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out
