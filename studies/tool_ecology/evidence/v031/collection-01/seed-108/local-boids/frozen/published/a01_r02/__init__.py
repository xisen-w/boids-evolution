"""Pure-Python services over lists of row dictionaries."""
from statistics import mean, median

def _fill(rows, method):
    values=[r.get('units') for r in rows if r.get('units') is not None]
    if method not in ('zero','mean','median'): raise ValueError('invalid fill')
    replacement=0 if method=='zero' or not values else mean(values) if method=='mean' else median(values)
    return [replacement if r.get('units') is None else r.get('units') for r in rows]

def _region(v): return v.strip().lower() if isinstance(v,str) else v

def clean(rows, lookup, request):
    units=_fill(rows,request.get('fill','zero'))
    out=[]
    for row,u in zip(rows,units):
        x=dict(row); x['region']=_region(row.get('region')); x['units']=u; out.append(x)
    return out

def _base(rows, request):
    out=clean(rows,None,request)
    for x in out:
        u,p=x.get('units'),x.get('price_cents')
        x['revenue_cents']=None if u is None or p is None else u*p
    return out

def revenue(rows, lookup, request): return _base(rows,request)

def _aggregate(vals, agg):
    vals=[v for v in vals if v is not None]
    if agg=='sum': return sum(vals)
    if agg=='count': return len(vals)
    if agg=='mean': return sum(vals)/len(vals) if vals else None
    raise ValueError('invalid aggregation')

def _group(rows,request,monthly=False):
    buckets={}
    for r in _base(rows,request):
        region=r.get('region'); date=r.get('date')
        if region is None or (monthly and date is None): continue
        key=(date[:7],region) if monthly else (region,)
        buckets.setdefault(key,[]).append(r['revenue_cents'])
    agg=request.get('agg','sum'); name=agg+'_revenue_cents'; out=[]
    for key in sorted(buckets,key=lambda k:tuple(str(v) for v in k)):
        row=({'month':key[0],'region':key[1]} if monthly else {'region':key[0]})
        row[name]=_aggregate(buckets[key],agg); out.append(row)
    return out

def group(rows,lookup,request): return _group(rows,request)
def monthly(rows,lookup,request): return _group(rows,request,True)
def lookup_service(rows,lookup,request):
    targets={_region(x.get('region')):x.get('target') for x in lookup}
    out=_base(rows,request)
    for x in out:
        t=targets.get(x.get('region')); v=x['revenue_cents']
        x['revenue_cents_per_target']=None if t is None or t==0 or v is None else v/t
    return out
def window(rows,lookup,request):
    n=request.get('window')
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    out=_base(rows,request)
    for i,x in enumerate(out):
        vals=[r['revenue_cents'] for r in out[max(0,i-n+1):i+1] if r['revenue_cents'] is not None]
        x['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out

def clean_service(rows,lookup,request): return clean(rows,lookup,request)
def revenue_service(rows,lookup,request): return revenue(rows,lookup,request)
def group_service(rows,lookup,request): return group(rows,lookup,request)
def monthly_service(rows,lookup,request): return monthly(rows,lookup,request)
def window_service(rows,lookup,request): return window(rows,lookup,request)
lookup=lookup_service
