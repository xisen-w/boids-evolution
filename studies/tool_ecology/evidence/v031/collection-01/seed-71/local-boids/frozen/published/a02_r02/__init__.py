"""Pure Python row-table service adapters."""

def _fill(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if method == 'zero' or not vals:
        value = 0
    elif method == 'mean':
        value = sum(vals) / len(vals)
    elif method == 'median':
        s = sorted(vals); n = len(s)
        value = s[n // 2] if n % 2 else (s[n//2-1] + s[n//2]) / 2
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [dict(r, units=value if r.get('units') is None else r.get('units')) for r in rows]

def clean(rows, lookup, request):
    out = _fill(rows, request.get('fill', 'zero'))
    for r in out:
        if r.get('region') is not None: r['region'] = r['region'].strip().lower()
    return out

def _base(rows, request):
    out = _fill(rows, request.get('fill', 'zero'))
    for r in out:
        if r.get('region') is not None: r['region'] = r['region'].strip().lower()
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u*p
    return out

def revenue(rows, lookup, request):
    # Revenue normalization preserves the source region spelling; only clean/grouped services normalize.
    out = _fill(rows, request.get('fill', 'zero'))
    for r in out:
        u,p=r.get('units'),r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u*p
    return out

def _aggregate(items, agg):
    vals=[v for v in items if v is not None]
    if agg=='sum': return sum(vals)
    if agg=='count': return len(vals)
    if agg=='mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")

def group(rows, lookup, request):
    data=_base(rows,request); groups={}
    for r in data:
        k=r.get('region')
        if k is not None: groups.setdefault(k,[]).append(r.get('revenue_cents'))
    agg=request.get('agg','sum'); name=agg+'_revenue_cents'
    return [{'region':k,name:_aggregate(v,agg)} for k,v in sorted(groups.items(),key=lambda p:str(p[0]))]

def monthly(rows, lookup, request):
    data=_base(rows,request); groups={}
    for r in data:
        date=r.get('date'); month=date[:7] if date is not None else None; region=r.get('region')
        if month is not None and region is not None: groups.setdefault((month,region),[]).append(r.get('revenue_cents'))
    agg=request.get('agg','sum'); name=agg+'_revenue_cents'
    return [{'month':m,'region':r,name:_aggregate(v,agg)} for (m,r),v in sorted(groups.items(),key=lambda p:(str(p[0][0]),str(p[0][1])))]

def lookup_service(rows, lookup, request):
    data=_base(rows,request)
    targets={r.get('region'):r.get('target') for r in lookup}
    for r in data:
        region=r.get('region'); target=targets.get(region); rev=r.get('revenue_cents')
        r['revenue_cents_per_target'] = rev/target if rev is not None and target not in (None,0) else None
    return data

def window(rows, lookup, request):
    out=_fill(rows,request.get('fill','zero'))
    for r in out:
        u,p=r.get('units'),r.get('price_cents'); r['revenue_cents']=None if u is None or p is None else u*p
    n=request.get('window',2)
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out

lookup = lookup_service
