"""Native implementations of the six table service families."""
from statistics import median

_MISSING = object()

def _fill(rows, mode):
    present = [r.get('units') for r in rows if r.get('units') is not None]
    if not present:
        return 0
    if mode == 'zero':
        return 0
    if mode == 'mean':
        return sum(present) / len(present)
    if mode == 'median':
        return median(present)
    raise ValueError("fill must be 'zero', 'mean', or 'median'")

def _region(value):
    return value.strip().lower() if isinstance(value, str) else value

def _filled_rows(rows, request, normalize=True):
    fill = _fill(rows, request.get('fill'))
    out=[]
    for row in rows:
        item=dict(row)
        if normalize:
            item['region']=_region(item.get('region'))
        if item.get('units') is None:
            item['units']=fill
        out.append(item)
    return out

def _revenue_rows(rows, request, normalize=True):
    out=_filled_rows(rows, request, normalize=normalize)
    for item in out:
        u,p=item.get('units'), item.get('price_cents')
        item['revenue_cents']=None if u is None or p is None else u*p
    return out

def clean(rows, lookup, request):
    return _filled_rows(rows, request)

def revenue(rows, lookup, request):
    return _revenue_rows(rows, request, normalize=False)

def _aggregate(rows, agg, keys):
    groups={}
    for row in rows:
        key=tuple(row.get(k) for k in keys)
        if any(v is None for v in key):
            continue
        groups.setdefault(key, []).append(row.get('revenue_cents'))
    result=[]
    for key, vals in groups.items():
        valid=[v for v in vals if v is not None]
        if agg == 'sum': value=sum(valid)
        elif agg == 'count': value=len(valid)
        elif agg == 'mean': value=sum(valid)/len(valid) if valid else None
        else: raise ValueError("agg must be 'sum', 'mean', or 'count'")
        if agg in ('sum','count') and not valid: value=0
        d=dict(zip(keys,key)); d[agg+'_revenue_cents']=value; result.append(d)
    result.sort(key=lambda d: tuple(str(d[k]) for k in keys))
    return result

def group(rows, lookup, request):
    return _aggregate(_revenue_rows(rows,request), request.get('agg'), ('region',))

def monthly(rows, lookup, request):
    data=_revenue_rows(rows,request)
    for item in data:
        date=item.get('date')
        item['month']=date[:7] if date is not None else None
    return _aggregate(data, request.get('agg'), ('month','region'))

def lookup(rows, lookup, request):
    data=_revenue_rows(rows,request)
    targets={_region(x.get('region')):x.get('target') for x in lookup}
    for item in data:
        target=targets.get(item.get('region'))
        value=item.get('revenue_cents')
        item['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value/target
    return data

def window(rows, lookup, request):
    data=_revenue_rows(rows,request, normalize=False)
    size=request.get('window')
    if size not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,item in enumerate(data):
        vals=[r['revenue_cents'] for r in data[max(0,i-size+1):i+1] if r['revenue_cents'] is not None]
        item['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return data
