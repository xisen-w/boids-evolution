"""Pure-Python transformations over list-of-dictionary row tables."""
from statistics import mean, median

def _base(rows, request):
    vals=[r['units'] for r in rows if r.get('units') is not None]
    method=request.get('fill','zero')
    if method=='zero' or not vals: fill=0
    elif method=='mean': fill=mean(vals)
    elif method=='median': fill=median(vals)
    else: raise ValueError("fill must be zero, mean, or median")
    out=[]
    for source in rows:
        r=dict(source)
        region=r.get('region')
        r['region']=region.strip().lower() if isinstance(region,str) else region
        if r.get('units') is None: r['units']=fill
        out.append(r)
    return out

def clean(rows, lookup, request):
    return _base(rows,request)

def revenue(rows, lookup, request):
    out=_base(rows,request)
    for r in out:
        u,p=r.get('units'),r.get('price_cents')
        r['revenue_cents']=None if u is None or p is None else u*p
    return out

def _agg(values, op):
    v=[x for x in values if x is not None]
    if op=='sum': return sum(v)
    if op=='count': return len(v)
    if op=='mean': return mean(v) if v else None
    raise ValueError('agg must be sum, mean, or count')

def _group(rows, request, monthly=False):
    buckets={}
    for r in revenue(rows,[],request):
        reg=r.get('region'); date=r.get('date'); month=date[:7] if date is not None else None
        if reg is None or (monthly and month is None): continue
        key=(month,reg) if monthly else (reg,)
        buckets.setdefault(key,[]).append(r['revenue_cents'])
    op=request.get('agg','sum'); out=[]
    for k in sorted(buckets,key=lambda x:tuple(map(str,x))):
        item={'month':k[0],'region':k[1]} if monthly else {'region':k[0]}
        item[op+'_revenue_cents']=_agg(buckets[k],op); out.append(item)
    return out

def group(rows, lookup, request): return _group(rows,request)
def monthly(rows, lookup, request): return _group(rows,request,True)

def lookup(rows, lookup, request):
    out=revenue(rows,lookup,request)
    targets={x.get('region'):x.get('target') for x in lookup}
    for r in out:
        t=targets.get(r.get('region')); v=r['revenue_cents']
        r['revenue_cents_per_target']=None if v is None or t is None or t==0 else v/t
    return out

def window(rows, lookup, request):
    out=revenue(rows,lookup,request); n=request.get('window')
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=mean(vals) if vals else None
    return out
