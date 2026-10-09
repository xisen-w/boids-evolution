"""Reliable row-oriented adapters; verified aggregation services reuse a01_r01."""
from statistics import mean, median
from published import a01_r01 as _base

def _fill(rows, request):
    vals=[r.get('units') for r in rows if r.get('units') is not None]
    mode=request.get('fill','zero')
    if mode not in ('zero','mean','median'): raise ValueError("fill must be zero, mean, or median")
    value=0 if not vals or mode=='zero' else mean(vals) if mode=='mean' else median(vals)
    out=[]
    for row in rows:
        r=dict(row)
        if r.get('units') is None: r['units']=value
        u,p=r.get('units'),r.get('price_cents')
        r['revenue_cents']=None if u is None or p is None else u*p
        out.append(r)
    return out

def clean(rows,lookup,request): return _base.clean(rows,lookup,request)
def revenue(rows,lookup,request): return _fill(rows,request)
def group(rows,lookup,request): return _base.group(rows,lookup,request)
def monthly(rows,lookup,request): return _base.monthly(rows,lookup,request)
def lookup(rows,lookup,request): return _base.lookup(rows,lookup,request)
def window(rows,lookup,request):
    out=_fill(rows,request); width=request.get('window',2)
    if width not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=mean(vals) if vals else None
    return out
