"""Reusable non-mutating services for row-oriented sales tables."""
from statistics import mean, median


def _fill(rows, mode):
    vals=[r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero': x=0
    elif mode == 'mean': x=mean(vals) if vals else 0
    elif mode == 'median': x=median(vals) if vals else 0
    else: raise ValueError("fill must be zero, mean, or median")
    return [dict(r, units=r.get('units') if r.get('units') is not None else x) for r in rows]

def _norm(v): return v.strip().lower() if isinstance(v,str) else v

def _revenue(rows, req):
    out=_fill(rows,req.get('fill','zero'))
    for r in out:
        u,p=r.get('units'),r.get('price_cents')
        r['revenue_cents']=u*p if u is not None and p is not None else None
    return out

def clean(rows, lookup, request):
    return [dict(r,region=_norm(r.get('region'))) for r in _fill(rows,request.get('fill','zero'))]

def revenue(rows, lookup, request): return _revenue(rows,request)

def _agg(vals, op):
    vals=[v for v in vals if v is not None]
    if op=='sum': return sum(vals)
    if op=='count': return len(vals)
    if op=='mean': return mean(vals) if vals else None
    raise ValueError('agg must be sum, mean, or count')

def group(rows, lookup, request):
    op=request.get('agg','sum'); groups={}
    for r in _revenue(rows,request):
        k=_norm(r.get('region'))
        if k is not None: groups.setdefault(k,[]).append(r['revenue_cents'])
    return [{'region':k,op+'_revenue_cents':_agg(groups[k],op)} for k in sorted(groups,key=str)]

def monthly(rows, lookup, request):
    op=request.get('agg','sum'); groups={}
    for r in _revenue(rows,request):
        m=r.get('date'); m=m[:7] if m is not None else None; k=_norm(r.get('region'))
        if m is not None and k is not None: groups.setdefault((m,k),[]).append(r['revenue_cents'])
    return [{'month':m,'region':k,op+'_revenue_cents':_agg(groups[(m,k)],op)} for m,k in sorted(groups,key=lambda x:(str(x[0]),str(x[1])))]

def lookup_service(rows, lookup, request):
    out=_revenue(rows,request); targets={_norm(x.get('region')):x.get('target') for x in lookup}
    for r in out:
        t=targets.get(_norm(r.get('region'))); v=r['revenue_cents']
        r['revenue_cents_per_target']=v/t if t not in (None,0) and v is not None else None
    return out

def window(rows, lookup, request):
    out=_revenue(rows,request); w=request.get('window')
    if w not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-w+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=mean(vals) if vals else None
    return out

lookup=lookup_service
