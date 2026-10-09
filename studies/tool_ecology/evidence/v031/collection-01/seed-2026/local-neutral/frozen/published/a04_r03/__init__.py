"""Pure-Python row transformations for six tabular service families."""
from statistics import mean, median


def _region(v):
    return None if v is None else v.strip().lower()

def _filled(rows, request):
    mode = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero': replacement = 0
    elif mode == 'mean': replacement = mean(vals) if vals else 0
    elif mode == 'median': replacement = median(vals) if vals else 0
    else: raise ValueError('fill must be zero, mean, or median')
    return [replacement if r.get('units') is None else r.get('units') for r in rows]

def clean(rows, lookup, request):
    out=[]
    for r,u in zip(rows,_filled(rows,request)):
        x=dict(r); x['region']=_region(r.get('region')); x['units']=u; out.append(x)
    return out

def revenue(rows, lookup, request):
    out=[]
    for r,u in zip(rows,_filled(rows,request)):
        x=dict(r); x['units']=u
        p=r.get('price_cents'); x['revenue_cents']=None if u is None or p is None else u*p
        out.append(x)
    return out

def _aggregate(values, agg):
    valid=[v for v in values if v is not None]
    if agg=='sum': return sum(valid) if valid else 0
    if agg=='count': return len(valid)
    if agg=='mean': return mean(valid) if valid else None
    raise ValueError('agg must be sum, mean, or count')

def _group(rows, request, by_month):
    data=revenue(rows,None,request); groups={}
    agg=request.get('agg','sum')
    if agg not in ('sum','mean','count'): raise ValueError('agg must be sum, mean, or count')
    for r in data:
        reg=_region(r.get('region')); date=r.get('date'); month=date[:7] if date is not None else None
        if reg is None or (by_month and month is None): continue
        key=(month,reg) if by_month else (reg,)
        groups.setdefault(key,[]).append(r['revenue_cents'])
    result=[]
    for key in sorted(groups, key=lambda k: tuple(str(v) for v in k)):
        value=_aggregate(groups[key],agg)
        result.append(({'month':key[0],'region':key[1]} if by_month else {'region':key[0]}) | {f'{agg}_revenue_cents':value})
    return result

def group(rows, lookup, request): return _group(rows,request,False)
def monthly(rows, lookup, request): return _group(rows,request,True)

def lookup(rows, lookup, request):
    data=revenue(rows,lookup,request)
    targets={entry.get('region'):entry.get('target') for entry in (lookup or [])}
    out=[]
    for r,x in zip(rows,data):
        region=_region(r.get('region')); target=targets.get(region); val=x['revenue_cents']; x['region']=region
        x['revenue_cents_per_target']=None if val is None or target is None or target==0 else val/target
        out.append(x)
    return out

def window(rows, lookup, request):
    width=request.get('window')
    if width not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    data=revenue(rows,lookup,request); values=[]; out=[]
    for i,x in enumerate(data):
        values.append(x['revenue_cents']); valid=[v for v in values[max(0,i-width+1):i+1] if v is not None]
        x['roll_revenue_cents']=mean(valid) if valid else None; out.append(x)
    return out
