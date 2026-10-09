"""Pure-Python implementations of row-table services."""
from statistics import mean, median


def _filled(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero': replacement = 0
    elif mode == 'mean': replacement = mean(vals) if vals else 0
    elif mode == 'median': replacement = median(vals) if vals else 0
    else: raise ValueError('fill must be zero, mean, or median')
    return [replacement if r.get('units') is None else r.get('units') for r in rows]


def _rev(rows, request, normalize=False):
    units = _filled(rows, request)
    out = []
    for row, unit in zip(rows, units):
        x = dict(row)
        x['units'] = unit
        if normalize and isinstance(x.get('region'), str): x['region'] = x['region'].strip().lower()
        p = row.get('price_cents')
        x['revenue_cents'] = None if unit is None or p is None else unit * p
        out.append(x)
    return out


def clean(rows, lookup, request):
    units = _filled(rows, request); out=[]
    for row, unit in zip(rows, units):
        x=dict(row); x['units']=unit
        if isinstance(x.get('region'), str): x['region']=x['region'].strip().lower()
        out.append(x)
    return out


def revenue(rows, lookup, request): return _rev(rows, request)


def _agg(vals, kind):
    v=[x for x in vals if x is not None]
    if kind == 'sum': return sum(v)
    if kind == 'count': return len(v)
    if kind == 'mean': return sum(v)/len(v) if v else None
    raise ValueError('agg must be sum, mean, or count')


def group(rows, lookup, request):
    gs={}
    for x in _rev(rows, request, True):
        k=x.get('region')
        if k is not None: gs.setdefault(k, []).append(x['revenue_cents'])
    a=request.get('agg', 'sum')
    return [{'region':k, a+'_revenue_cents':_agg(gs[k],a)} for k in sorted(gs,key=str)]


def monthly(rows, lookup, request):
    gs={}
    for x in _rev(rows, request, True):
        d=x.get('date'); m=d[:7] if d is not None else None; r=x.get('region')
        if m is not None and r is not None: gs.setdefault((m,r),[]).append(x['revenue_cents'])
    a=request.get('agg','sum')
    return [{'month':m,'region':r,a+'_revenue_cents':_agg(gs[(m,r)],a)} for m,r in sorted(gs,key=lambda z:(str(z[0]),str(z[1])))]


def lookup_service(rows, lookup, request):
    out=_rev(rows,request,True)
    targets={x.get('region'):x.get('target') for x in lookup if x.get('region') is not None}
    for x in out:
        t=targets.get(x.get('region')); v=x['revenue_cents']
        x['revenue_cents_per_target']=None if t is None or t == 0 or v is None else v/t
    return out


def window(rows, lookup, request):
    out=_rev(rows,request); w=request.get('window')
    if w not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,x in enumerate(out):
        vals=[z['revenue_cents'] for z in out[max(0,i-w+1):i+1] if z['revenue_cents'] is not None]
        x['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out
