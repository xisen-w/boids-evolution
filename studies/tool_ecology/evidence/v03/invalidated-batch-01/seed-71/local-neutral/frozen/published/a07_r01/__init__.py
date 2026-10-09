"""Reusable row-oriented services for small sales tables."""
from statistics import median

_MISSING = object()

def _region(value):
    return value.strip().lower() if isinstance(value, str) else value

def _fill_value(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero': return 0
    if not vals: return 0
    if mode == 'mean': return sum(vals) / len(vals)
    if mode == 'median': return median(vals)
    raise ValueError("fill must be 'zero', 'mean', or 'median'")

def _prepare(rows, request, normalize=True):
    rows = list(rows)
    fill = _fill_value(rows, request.get('fill', 'zero'))
    out=[]
    for original in rows:
        r=dict(original)
        if normalize: r['region'] = _region(r.get('region'))
        if r.get('units') is None: r['units']=fill
        a,b=r.get('units'),r.get('price_cents')
        r['revenue_cents'] = None if a is None or b is None else a*b
        out.append(r)
    return out

def _agg(vals, op):
    present=[x for x in vals if x is not None]
    if op == 'sum': return sum(present)
    if op == 'count': return len(present)
    if op == 'mean': return sum(present)/len(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")

def clean(rows, lookup, request):
    fill=_fill_value(rows, request.get('fill','zero'))
    out=[]
    for original in rows:
        r=dict(original)
        r['region']=_region(r.get('region'))
        if r.get('units') is None: r['units']=fill
        out.append(r)
    return out

def revenue(rows, lookup, request):
    return _prepare(rows,request)

def _groups(rows, request, keys):
    op=request.get('agg','sum')
    groups={}
    for r in rows:
        k=tuple(r.get(x) for x in keys)
        if any(x is None for x in k): continue
        groups.setdefault(k,[]).append(r.get('revenue_cents'))
    result=[]
    for k, vals in groups.items():
        result.append(dict(zip(keys,k), **{op+'_revenue_cents':_agg(vals,op)}))
    result.sort(key=lambda r: tuple(str(r[x]) for x in keys))
    return result

def group(rows, lookup, request):
    return _groups(_prepare(rows,request),request,['region'])

def monthly(rows, lookup, request):
    prepared=_prepare(rows,request)
    for r in prepared:
        date=r.get('date')
        r['month']=date[:7] if date is not None else None
    return _groups(prepared,request,['month','region'])

def lookup(rows, lookup, request):
    out=_prepare(rows,request)
    targets={_region(x.get('region')):x.get('target') for x in lookup}
    for r in out:
        target=targets.get(r.get('region'))
        revenue_value=r.get('revenue_cents')
        r['revenue_cents_per_target'] = (None if target is None or target == 0 or revenue_value is None else revenue_value/target)
    return out

def window(rows, lookup, request):
    out=_prepare(rows,request,normalize=False)
    width=request.get('window')
    if width not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out
