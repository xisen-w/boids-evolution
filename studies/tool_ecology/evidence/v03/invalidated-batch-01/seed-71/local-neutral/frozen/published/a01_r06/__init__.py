"""Pure-Python tabular service adapters."""
from statistics import mean, median

def _fill(rows, request):
    vals=[r.get('units') for r in rows if r.get('units') is not None]
    mode=request.get('fill','zero')
    replacement=0 if not vals or mode=='zero' else (mean(vals) if mode=='mean' else median(vals))
    return [replacement if r.get('units') is None else r.get('units') for r in rows]

def _base(rows, request):
    units=_fill(rows,request); out=[]
    for r,u in zip(rows,units):
        x=dict(r); x['region']=r.get('region').strip().lower() if isinstance(r.get('region'),str) else r.get('region'); x['units']=u
        p=r.get('price_cents'); x['revenue_cents']=None if u is None or p is None else u*p
        out.append(x)
    return out

def clean(rows, lookup, request):
    units=_fill(rows,request); out=[]
    for r,u in zip(rows,units):
        x=dict(r); x['region']=r.get('region').strip().lower() if isinstance(r.get('region'),str) else r.get('region'); x['units']=u; out.append(x)
    return out

def revenue(rows, lookup, request): return _base(rows,request)

def _aggregate(values, agg):
    vals=[v for v in values if v is not None]
    if agg=='count': return len(vals)
    if agg=='mean': return sum(vals)/len(vals) if vals else None
    return sum(vals)

def _group(rows, request, monthly):
    data=_base(rows,request); groups={}
    for r in data:
        region=r.get('region'); month=r.get('date')[:7] if isinstance(r.get('date'),str) else None
        key=(month,region) if monthly else (region,)
        if any(k is None for k in key): continue
        groups.setdefault(key,[]).append(r['revenue_cents'])
    agg=request.get('agg','sum'); result=[]
    for key in sorted(groups,key=lambda k:tuple(str(v) for v in k)):
        row={}
        if monthly: row['month']=key[0]; row['region']=key[1]
        else: row['region']=key[0]
        row[agg+'_revenue_cents']=_aggregate(groups[key],agg); result.append(row)
    return result

def group(rows, lookup, request): return _group(rows,request,False)
def monthly(rows, lookup, request): return _group(rows,request,True)

def lookup(rows, lookup_rows, request):
    data=_base(rows,request); targets={r.get('region'):r.get('target') for r in lookup_rows}
    for r in data:
        target=targets.get(r.get('region')); value=r.get('revenue_cents')
        r['revenue_cents_per_target']=None if target is None or target==0 or value is None else value/target
    return data

def window(rows, lookup, request):
    data=_base(rows,request); n=request.get('window',2); vals=[]
    for i,r in enumerate(data):
        vals.append(r['revenue_cents']); recent=[v for v in vals[max(0,i-n+1):i+1] if v is not None]
        r['roll_revenue_cents']=sum(recent)/len(recent) if recent else None
    return data
