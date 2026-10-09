"""Native implementations of the recurring table services."""
from statistics import mean, median


def _fill(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if method == 'zero': value = 0
    elif not vals: value = 0
    elif method == 'mean': value = mean(vals)
    elif method == 'median': value = median(vals)
    else: raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [value if r.get('units') is None else r.get('units') for r in rows]


def _region(value):
    return value.strip().lower() if isinstance(value, str) else None


def _base(rows, request):
    units = _fill(rows, request.get('fill'))
    out = []
    for r, u in zip(rows, units):
        x = dict(r)
        x['region'] = _region(r.get('region'))
        x['units'] = u
        rev = None if u is None or r.get('price_cents') is None else u * r['price_cents']
        x['revenue_cents'] = rev
        out.append(x)
    return out


def clean(rows, lookup, request):
    units = _fill(rows, request.get('fill'))
    out=[]
    for r,u in zip(rows,units):
        x=dict(r); x['region']=_region(r.get('region')); x['units']=u; out.append(x)
    return out


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(values, agg):
    vals=[v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    groups={}
    for r in _base(rows,request):
        k=r['region']
        if k is not None: groups.setdefault(k,[]).append(r['revenue_cents'])
    agg=request.get('agg')
    return [{'region':k, agg+'_revenue_cents':_aggregate(v,agg)} for k,v in sorted(groups.items(),key=lambda kv:str(kv[0]))]


def monthly(rows, lookup, request):
    groups={}
    for r in _base(rows,request):
        date=r.get('date'); month=date[:7] if date is not None else None; region=r['region']
        if month is not None and region is not None: groups.setdefault((month,region),[]).append(r['revenue_cents'])
    agg=request.get('agg')
    return [{'month':m,'region':r,agg+'_revenue_cents':_aggregate(v,agg)} for (m,r),v in sorted(groups.items(),key=lambda kv:(str(kv[0][0]),str(kv[0][1])))]


def lookup(rows, lookup, request):
    out=_base(rows,request)
    targets={_region(x.get('region')):x.get('target') for x in lookup if _region(x.get('region')) is not None}
    for r in out:
        target=targets.get(r['region']); rev=r['revenue_cents']
        r['revenue_cents_per_target']=None if target is None or target == 0 or rev is None else rev/target
    return out


def window(rows, lookup, request):
    out=_base(rows,request); w=request.get('window')
    if w not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-w+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out
