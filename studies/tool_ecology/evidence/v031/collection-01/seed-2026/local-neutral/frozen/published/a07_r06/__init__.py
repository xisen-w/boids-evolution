"""Pure-Python row-oriented table services."""
from statistics import median


def _region(v):
    return v.strip().lower() if isinstance(v, str) else v


def _filled(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero' or not vals:
        value = 0
    elif mode == 'mean':
        value = sum(vals) / len(vals)
    elif mode == 'median':
        value = median(vals)
    else:
        raise ValueError("fill must be zero, mean, or median")
    return [value if r.get('units') is None else r.get('units') for r in rows]


def _base(rows, request):
    units = _filled(rows, request.get('fill', 'zero'))
    out=[]
    for r,u in zip(rows, units):
        x=dict(r)
        x['region']=_region(x.get('region'))
        x['units']=u
        x['revenue_cents']=None if u is None or x.get('price_cents') is None else u*x['price_cents']
        out.append(x)
    return out


def clean(rows, lookup, request):
    units=_filled(rows, request.get('fill','zero'))
    return [dict(r, region=_region(r.get('region')), units=u) for r,u in zip(rows,units)]


def revenue(rows, lookup, request):
    return _base(rows,request)


def _aggregate(vals, agg):
    present=[v for v in vals if v is not None]
    if agg=='sum': return sum(present)
    if agg=='count': return len(present)
    if agg=='mean': return sum(present)/len(present) if present else None
    raise ValueError('agg must be sum, mean, or count')


def group(rows, lookup, request):
    d={}
    for r in _base(rows,request):
        k=r.get('region')
        if k is not None: d.setdefault(k,[]).append(r['revenue_cents'])
    agg=request.get('agg','sum')
    return [{'region':k, agg+'_revenue_cents':_aggregate(d[k],agg)} for k in sorted(d,key=str)]


def monthly(rows, lookup, request):
    d={}
    for r in _base(rows,request):
        date=r.get('date'); region=r.get('region')
        month=date[:7] if date is not None else None
        if month is not None and region is not None:
            d.setdefault((month,region),[]).append(r['revenue_cents'])
    agg=request.get('agg','sum')
    return [{'month':m,'region':r,agg+'_revenue_cents':_aggregate(d[(m,r)],agg)} for m,r in sorted(d,key=lambda k:(str(k[0]),str(k[1])))]


def lookup(rows, lookup, request):
    targets={x.get('region'):x.get('target') for x in lookup}
    out=_base(rows,request)
    for x in out:
        t=targets.get(x.get('region'))
        v=x['revenue_cents']
        x['revenue_cents_per_target']=None if t is None or t==0 or v is None else v/t
    return out


def window(rows, lookup, request):
    out=_base(rows,request)
    w=request.get('window',2)
    if w not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,x in enumerate(out):
        vals=[r['revenue_cents'] for r in out[max(0,i-w+1):i+1] if r['revenue_cents'] is not None]
        x['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out
