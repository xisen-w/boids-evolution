"""Small, dependency-free row-oriented implementations of the publication services."""
from statistics import median


def _fill(rows, mode):
    values = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero' or not values:
        replacement = 0
    elif mode == 'mean':
        replacement = sum(values) / len(values)
    elif mode == 'median':
        replacement = median(values)
    else:
        raise ValueError("request.fill must be 'zero', 'mean', or 'median'")
    return [replacement if r.get('units') is None else r.get('units') for r in rows]


def _base(rows, request):
    units = _fill(rows, request.get('fill'))
    out = []
    for row, unit in zip(rows, units):
        x = dict(row)
        x['region'] = row.get('region').strip().lower() if row.get('region') is not None else None
        x['units'] = unit
        revenue = None if unit is None or row.get('price_cents') is None else unit * row['price_cents']
        x['revenue_cents'] = revenue
        out.append(x)
    return out


def clean(rows, lookup, request):
    units = _fill(rows, request.get('fill'))
    out=[]
    for r,u in zip(rows,units):
        x=dict(r); x['region']=r.get('region').strip().lower() if r.get('region') is not None else None; x['units']=u; out.append(x)
    return out


def revenue(rows, lookup, request):
    return _base(rows, request)


def _agg(values, kind):
    vals=[v for v in values if v is not None]
    if kind == 'sum': return sum(vals)
    if kind == 'count': return len(vals)
    if kind == 'mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("request.agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    kind=request.get('agg'); grouped={}
    for r in _base(rows,request):
        key=r['region']
        if key is not None: grouped.setdefault(key,[]).append(r['revenue_cents'])
    col=kind+'_revenue_cents'
    return [{'region':k, col:_agg(grouped[k],kind)} for k in sorted(grouped,key=str)]


def monthly(rows, lookup, request):
    kind=request.get('agg'); grouped={}
    for r in _base(rows,request):
        date=r.get('date'); month=date[:7] if date is not None else None; region=r['region']
        if month is not None and region is not None: grouped.setdefault((month,region),[]).append(r['revenue_cents'])
    col=kind+'_revenue_cents'
    return [{'month':m,'region':r,col:_agg(grouped[(m,r)],kind)} for m,r in sorted(grouped,key=lambda k:(str(k[0]),str(k[1])))]


def lookup(rows, lookup, request):
    data=_base(rows,request)
    targets={r.get('region'):r.get('target') for r in lookup}
    for r in data:
        target=targets.get(r['region']); value=r['revenue_cents']
        r['revenue_cents_per_target'] = value/target if value is not None and target not in (None,0) else None
    return data


def window(rows, lookup, request):
    data=_base(rows,request); n=request.get('window')
    if n not in (2,3,4): raise ValueError('request.window must be 2, 3, or 4')
    for i,r in enumerate(data):
        vals=[x['revenue_cents'] for x in data[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return data
