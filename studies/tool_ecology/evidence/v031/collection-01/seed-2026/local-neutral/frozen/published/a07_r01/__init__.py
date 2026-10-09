"""Native dataframe-free adapters for the six tabular service families."""
from statistics import mean, median

_MISSING = object()

def _fill_units(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = 0 if not vals else (sum(vals)/len(vals) if method == 'mean' else median(vals) if method == 'median' else 0)
    out=[]
    for row in rows:
        d=dict(row)
        if d.get('units') is None: d['units']=replacement
        out.append(d)
    return out

def _norm(x):
    return x.strip().lower() if isinstance(x,str) else x

def clean(rows, lookup, request):
    out=_fill_units(rows, request.get('fill','zero'))
    for d in out: d['region']=_norm(d.get('region'))
    return out

def _base(rows, request):
    out=_fill_units(rows, request.get('fill','zero'))
    for d in out:
        d['region']=_norm(d.get('region'))
        u,p=d.get('units'),d.get('price_cents')
        d['revenue_cents']=None if u is None or p is None else u*p
    return out

def revenue(rows, lookup, request):
    return _base(rows,request)

def _aggregate(vals, agg):
    good=[v for v in vals if v is not None]
    if agg=='count': return len(good)
    if agg=='mean': return sum(good)/len(good) if good else None
    return sum(good)

def group(rows, lookup, request):
    data=_base(rows,request); groups={}
    for d in data:
        k=d.get('region')
        if k is not None: groups.setdefault(k,[]).append(d.get('revenue_cents'))
    agg=request.get('agg','sum'); key=agg+'_revenue_cents'
    return [{'region':k,key:_aggregate(v,agg)} for k,v in sorted(groups.items(),key=lambda item:str(item[0]))]

def monthly(rows, lookup, request):
    data=_base(rows,request); groups={}
    for d in data:
        date=d.get('date'); month=date[:7] if date is not None else None; region=d.get('region')
        if month is not None and region is not None: groups.setdefault((month,region),[]).append(d.get('revenue_cents'))
    agg=request.get('agg','sum'); key=agg+'_revenue_cents'
    return [{'month':m,'region':r,key:_aggregate(v,agg)} for (m,r),v in sorted(groups.items(),key=lambda item:(str(item[0][0]),str(item[0][1])))]

def lookup_service(rows, lookup, request):
    data=_base(rows,request)
    targets={_norm(x.get('region')):x.get('target') for x in lookup if x.get('region') is not None}
    for d in data:
        target=targets.get(d.get('region')); rev=d.get('revenue_cents')
        d['revenue_cents_per_target']=None if target is None or target==0 or rev is None else rev/target
    return data

def window(rows, lookup, request):
    data=_base(rows,request); n=request.get('window',2); vals=[]
    for i,d in enumerate(data):
        vals.append(d.get('revenue_cents'))
        current=vals[max(0,i-n+1):i+1]; good=[v for v in current if v is not None]
        d['roll_revenue_cents']=sum(good)/len(good) if good else None
    return data

# Root-level adapters named explicitly by publish metadata.
lookup=lookup_service
