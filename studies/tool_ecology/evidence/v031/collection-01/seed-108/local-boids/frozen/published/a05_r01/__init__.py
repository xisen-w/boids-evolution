"""Native implementations of the recurring table services."""
from statistics import mean, median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _base(rows, request):
    """Copy rows, normalize region, fill units, append revenue."""
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    fill = {'zero': 0, 'mean': (sum(vals) / len(vals) if vals else 0),
            'median': (median(vals) if vals else 0)}.get(mode)
    if fill is None:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out=[]
    for row in rows:
        x=dict(row)
        x['region']=_region(x.get('region'))
        units=x.get('units')
        if units is None:
            units=fill
            x['units']=units
        p=x.get('price_cents')
        x['revenue_cents']=None if units is None or p is None else units*p
        out.append(x)
    return out


def clean(rows, lookup, request):
    """Normalize region and fill units; preserve the input columns and order."""
    vals=[r.get('units') for r in rows if r.get('units') is not None]
    mode=request.get('fill','zero')
    if mode=='zero': fill=0
    elif mode=='mean': fill=sum(vals)/len(vals) if vals else 0
    elif mode=='median': fill=median(vals) if vals else 0
    else: raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out=[]
    for row in rows:
        x=dict(row); x['region']=_region(x.get('region'))
        if x.get('units') is None: x['units']=fill
        out.append(x)
    return out


def revenue(rows, lookup, request):
    """Fill units and append revenue_cents."""
    return _base(rows, request)


def _aggregate(values, agg):
    present=[v for v in values if v is not None]
    if agg=='sum': return sum(present)
    if agg=='count': return len(present)
    if agg=='mean': return sum(present)/len(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    """Aggregate revenue by normalized, nonmissing region."""
    data=_base(rows, request); buckets={}
    for r in data:
        key=r.get('region')
        if key is not None: buckets.setdefault(key, []).append(r['revenue_cents'])
    agg=request.get('agg','sum')
    return [{'region':k, f'{agg}_revenue_cents':_aggregate(v,agg)}
            for k,v in sorted(buckets.items(), key=lambda kv:str(kv[0]))]


def monthly(rows, lookup, request):
    """Aggregate revenue by YYYY-MM and normalized region."""
    data=_base(rows, request); buckets={}
    for r in data:
        date=r.get('date'); region=r.get('region')
        month=date[:7] if date is not None else None
        if month is not None and region is not None:
            buckets.setdefault((month,region), []).append(r['revenue_cents'])
    agg=request.get('agg','sum')
    keys=sorted(buckets, key=lambda k:(str(k[0]),str(k[1])))
    return [{'month':m, 'region':r, f'{agg}_revenue_cents':_aggregate(buckets[(m,r)],agg)} for m,r in keys]


def lookup(rows, lookup, request):
    """Add per-target revenue using an exact normalized region key."""
    data=_base(rows, request)
    targets={_region(x.get('region')):x.get('target') for x in lookup}
    for r in data:
        t=targets.get(r.get('region')); rev=r.get('revenue_cents')
        r['revenue_cents_per_target'] = rev/t if rev is not None and t not in (None,0) else None
    return data


def window(rows, lookup, request):
    """Append trailing ROWS-window mean of nonmissing revenue."""
    data=_base(rows, request); n=request.get('window')
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(data):
        vals=[x['revenue_cents'] for x in data[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return data
