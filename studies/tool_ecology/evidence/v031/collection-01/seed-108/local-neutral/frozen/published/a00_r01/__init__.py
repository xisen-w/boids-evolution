"""Native implementations of the recurring table services."""
from statistics import mean, median

_MISSING = object()


def _fill_units(rows, mode):
    values = [r.get('units') for r in rows if r.get('units') is not None]
    if not values:
        replacement = 0
    elif mode == 'zero':
        replacement = 0
    elif mode == 'mean':
        replacement = mean(values)
    elif mode == 'median':
        replacement = median(values)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [replacement if r.get('units') is None else r.get('units') for r in rows]


def _prepare(rows, request):
    units = _fill_units(rows, request.get('fill'))
    out = []
    for row, u in zip(rows, units):
        item = dict(row)
        item['region'] = row.get('region').strip().lower() if isinstance(row.get('region'), str) else row.get('region')
        item['units'] = u
        price = row.get('price_cents')
        item['revenue_cents'] = None if u is None or price is None else u * price
        out.append(item)
    return out


def clean(rows, lookup, request):
    units = _fill_units(rows, request.get('fill'))
    out=[]
    for row,u in zip(rows, units):
        item=dict(row)
        item['region'] = row.get('region').strip().lower() if isinstance(row.get('region'), str) else row.get('region')
        item['units']=u
        out.append(item)
    return out


def revenue(rows, lookup, request):
    return _prepare(rows, request)


def _aggregate(values, agg):
    vals=[v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    data=_prepare(rows,request); buckets={}
    for row in data:
        key=row['region']
        if key is not None: buckets.setdefault(key,[]).append(row['revenue_cents'])
    agg=request.get('agg')
    return [{'region':k, f'{agg}_revenue_cents':_aggregate(v,agg)} for k,v in sorted(buckets.items(),key=lambda p:str(p[0]))]


def monthly(rows, lookup, request):
    data=_prepare(rows,request); buckets={}
    for row in data:
        date=row.get('date'); region=row['region']
        month=date[:7] if date is not None else None
        if month is not None and region is not None:
            buckets.setdefault((month,region),[]).append(row['revenue_cents'])
    agg=request.get('agg')
    return [{'month':m,'region':r,f'{agg}_revenue_cents':_aggregate(v,agg)} for (m,r),v in sorted(buckets.items(),key=lambda p:(str(p[0][0]),str(p[0][1])))]


def lookup(rows, lookup, request):
    data=_prepare(rows,request)
    targets={item.get('region'):item.get('target') for item in lookup}
    for row in data:
        target=targets.get(row['region'],_MISSING)
        value=row['revenue_cents']
        row['revenue_cents_per_target'] = None if target is _MISSING or target is None or target == 0 or value is None else value/target
    return data


def window(rows, lookup, request):
    data=_prepare(rows,request); n=request.get('window')
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,row in enumerate(data):
        vals=[x['revenue_cents'] for x in data[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        row['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return data
