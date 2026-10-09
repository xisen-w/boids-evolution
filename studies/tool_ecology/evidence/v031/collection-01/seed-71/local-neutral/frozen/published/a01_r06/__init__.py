"""Small, non-mutating sales table transforms."""
from statistics import mean, median


def _units(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    fill = 0 if not vals else (mean(vals) if mode == 'mean' else median(vals) if mode == 'median' else 0)
    return [fill if r.get('units') is None else r.get('units') for r in rows]


def clean(rows, lookup, request):
    units = _units(rows, request)
    out=[]
    for r,u in zip(rows, units):
        x=dict(r); x['region'] = r.get('region').strip().lower() if r.get('region') is not None else None; x['units']=u; out.append(x)
    return out


def revenue(rows, lookup, request):
    base=clean(rows, lookup, request); out=[]
    for x in base:
        p=x.get('price_cents'); u=x.get('units'); x['revenue_cents'] = None if p is None or u is None else u*p; out.append(x)
    return out


def _aggregate(vals, agg):
    vals=[v for v in vals if v is not None]
    if agg=='count': return len(vals)
    if agg=='mean': return mean(vals) if vals else None
    return sum(vals)


def group(rows, lookup, request):
    buckets={}
    for x in revenue(rows, lookup, request):
        k=x.get('region')
        if k is not None: buckets.setdefault(k, []).append(x['revenue_cents'])
    agg=request.get('agg','sum')
    return [{'region':k, agg+'_revenue_cents':_aggregate(buckets[k],agg)} for k in sorted(buckets,key=str)]


def monthly(rows, lookup, request):
    buckets={}
    for x in revenue(rows, lookup, request):
        region=x.get('region'); date=x.get('date'); month=date[:7] if date is not None else None
        if region is not None and month is not None: buckets.setdefault((month,region),[]).append(x['revenue_cents'])
    agg=request.get('agg','sum')
    return [{'month':m,'region':r,agg+'_revenue_cents':_aggregate(buckets[(m,r)],agg)} for m,r in sorted(buckets,key=lambda k:(str(k[0]),str(k[1])))]


def lookup(rows, lookup, request):
    targets={(x.get('region').strip().lower() if x.get('region') is not None else None):x.get('target') for x in lookup}
    out=[]
    for x in revenue(rows,lookup,request):
        t=targets.get(x.get('region')); v=x.get('revenue_cents')
        x['revenue_cents_per_target']=None if t is None or t==0 or v is None else v/t
        out.append(x)
    return out


def window(rows, lookup, request):
    out=revenue(rows,lookup,request); n=request.get('window',2)
    vals=[]
    for i,x in enumerate(out):
        vals.append(x.get('revenue_cents'))
        recent=[v for v in vals[max(0,i-n+1):i+1] if v is not None]
        x['roll_revenue_cents']=mean(recent) if recent else None
    return out
