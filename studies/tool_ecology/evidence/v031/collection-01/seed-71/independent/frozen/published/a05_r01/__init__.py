"""Reusable native-Python implementations of the tabular service families."""
from statistics import median

_MISSING = object()

def _fill(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero': value = 0
    elif not vals: value = 0
    elif mode == 'mean': value = sum(vals) / len(vals)
    elif mode == 'median': value = median(vals)
    else: raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [value if r.get('units') is None else r.get('units') for r in rows]

def _base(rows, request):
    units = _fill(rows, request.get('fill', 'zero'))
    out=[]
    for row, u in zip(rows, units):
        d=dict(row)
        reg=row.get('region')
        d['region'] = reg.strip().lower() if isinstance(reg, str) else reg
        d['units']=u
        p=row.get('price_cents')
        d['revenue_cents']=None if u is None or p is None else u*p
        out.append(d)
    return out

def clean(rows, lookup, request):
    units=_fill(rows, request.get('fill','zero'))
    out=[]
    for row,u in zip(rows,units):
        d=dict(row); reg=row.get('region'); d['region']=reg.strip().lower() if isinstance(reg,str) else reg; d['units']=u; out.append(d)
    return out

def revenue(rows, lookup, request): return _base(rows,request)

def _aggregate(values, agg):
    vals=[v for v in values if v is not None]
    if agg=='sum': return sum(vals)
    if agg=='count': return len(vals)
    if agg=='mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")

def group(rows, lookup, request):
    data=_base(rows,request); groups={}
    for r in data:
        key=r['region']
        if key is not None: groups.setdefault(key,[]).append(r['revenue_cents'])
    agg=request.get('agg','sum')
    return [{'region':k,agg+'_revenue_cents':_aggregate(groups[k],agg)} for k in sorted(groups,key=str)]

def monthly(rows, lookup, request):
    data=_base(rows,request); groups={}
    for r in data:
        month=r.get('date'); month=month[:7] if month is not None else None
        reg=r['region']
        if month is not None and reg is not None: groups.setdefault((month,reg),[]).append(r['revenue_cents'])
    agg=request.get('agg','sum')
    return [{'month':m,'region':r,agg+'_revenue_cents':_aggregate(groups[(m,r)],agg)} for m,r in sorted(groups,key=lambda x:(str(x[0]),str(x[1])))]

def lookup(rows, lookup, request):
    data=_base(rows,request); targets={}
    for entry in lookup:
        reg=entry.get('region'); key=reg.strip().lower() if isinstance(reg,str) else reg
        targets[key]=entry.get('target')
    for r in data:
        target=targets.get(r['region'],_MISSING); value=r['revenue_cents']
        r['revenue_cents_per_target']=None if target is _MISSING or target is None or target==0 or value is None else value/target
    return data

def window(rows, lookup, request):
    data=_base(rows,request); w=request.get('window',2)
    if w not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    vals=[]
    for i,r in enumerate(data):
        vals.append(r['revenue_cents'])
        present=[v for v in vals[max(0,i-w+1):i+1] if v is not None]
        r['roll_revenue_cents']=sum(present)/len(present) if present else None
    return data

__all__=['clean','revenue','group','monthly','lookup','window']
