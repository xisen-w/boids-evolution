"""Pure Python table services. Inputs are lists of row dictionaries; inputs are never mutated."""
from statistics import median

def _fill(rows, request):
    vals=[r.get('units') for r in rows if r.get('units') is not None]
    mode=request.get('fill','zero')
    replacement=0 if not vals or mode=='zero' else (sum(vals)/len(vals) if mode=='mean' else median(vals))
    return [replacement if r.get('units') is None else r.get('units') for r in rows]

def _base(rows, request):
    units=_fill(rows,request); out=[]
    for row,u in zip(rows,units):
        r=dict(row); r['units']=u
        if r.get('region') is not None: r['region']=r['region'].strip().lower()
        a,b=r.get('units'),r.get('price_cents')
        r['revenue_cents']=None if a is None or b is None else a*b
        out.append(r)
    return out

def clean(rows, lookup, request):
    units=_fill(rows,request); out=[]
    for row,u in zip(rows,units):
        r=dict(row); r['units']=u
        if r.get('region') is not None:r['region']=r['region'].strip().lower()
        out.append(r)
    return out

def revenue(rows, lookup, request): return _base(rows,request)

def _aggregate(items, agg):
    vals=[x for x in items if x is not None]
    if agg=='count': return len(vals)
    if agg=='sum': return sum(vals)
    return sum(vals)/len(vals) if vals else None

def _groups(rows, request, monthly=False):
    agg=request.get('agg','sum'); groups={}
    for r in _base(rows,request):
        region=r.get('region'); month=r.get('date')[:7] if r.get('date') is not None else None
        if region is None or (monthly and month is None): continue
        key=(month,region) if monthly else (region,)
        groups.setdefault(key,[]).append(r['revenue_cents'])
    result=[]
    for key in sorted(groups,key=lambda k:tuple(str(x) for x in k)):
        row=({'month':key[0],'region':key[1]} if monthly else {'region':key[0]})
        row[agg+'_revenue_cents']=_aggregate(groups[key],agg); result.append(row)
    return result

def group(rows, lookup, request): return _groups(rows,request)
def monthly(rows, lookup, request): return _groups(rows,request,True)

def lookup(rows, lookup, request):
    targets={r.get('region'):r.get('target') for r in lookup}
    out=[]
    for r in _base(rows,request):
        target=targets.get(r.get('region'))
        r['revenue_cents_per_target']=None if target is None or target==0 or r['revenue_cents'] is None else r['revenue_cents']/target
        out.append(r)
    return out

def window(rows, lookup, request):
    out=_base(rows,request); width=request.get('window',2)
    for i,r in enumerate(out):
        values=[x['revenue_cents'] for x in out[max(0,i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(values)/len(values) if values else None
    return out
