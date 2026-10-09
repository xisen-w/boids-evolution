"""Native implementations of the recurring table services."""
from statistics import mean, median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _base(rows, request):
    """Copy rows, normalize region, impute units, and derive revenue."""
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    fill = request.get('fill', 'zero')
    if fill == 'zero' or not vals:
        replacement = 0
    elif fill == 'mean':
        replacement = mean(vals)
    elif fill == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out = []
    for row in rows:
        r = dict(row)
        r['region'] = _region(r.get('region'))
        units = r.get('units')
        if units is None:
            units = replacement
            r['units'] = units
        price = r.get('price_cents')
        r['revenue_cents'] = None if units is None or price is None else units * price
        out.append(r)
    return out


def clean(rows, lookup, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    f = request.get('fill', 'zero')
    if f not in ('zero','mean','median'): raise ValueError('invalid fill')
    v = 0 if not vals else (mean(vals) if f == 'mean' else median(vals) if f == 'median' else 0)
    out=[]
    for row in rows:
        r=dict(row); r['region']=_region(r.get('region'))
        if r.get('units') is None: r['units']=v
        out.append(r)
    return out


def revenue(rows, lookup, request):
    return _base(rows, request)


def _agg(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    data = _base(rows, request); agg=request.get('agg','sum'); groups={}
    for r in data:
        key=r.get('region')
        if key is not None: groups.setdefault(key, []).append(r['revenue_cents'])
    return [{'region':k, agg+'_revenue_cents':_agg(groups[k],agg)} for k in sorted(groups,key=str)]


def monthly(rows, lookup, request):
    data=_base(rows,request); agg=request.get('agg','sum'); groups={}
    for r in data:
        month = r.get('date')
        month = month[:7] if month is not None else None
        region=r.get('region')
        if month is not None and region is not None:
            groups.setdefault((month,region),[]).append(r['revenue_cents'])
    return [{'month':m,'region':reg,agg+'_revenue_cents':_agg(groups[(m,reg)],agg)}
            for m,reg in sorted(groups,key=lambda x:(str(x[0]),str(x[1])))]


def lookup(rows, lookup, request):
    data=_base(rows,request)
    targets={_region(x.get('region')):x.get('target') for x in lookup if x.get('region') is not None}
    for r in data:
        target=targets.get(r.get('region')); rev=r['revenue_cents']
        r['revenue_cents_per_target'] = rev/target if rev is not None and target not in (None,0) else None
    return data


def window(rows, lookup, request):
    data=_base(rows,request); n=request.get('window')
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(data):
        vals=[x['revenue_cents'] for x in data[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return data

__all__=['clean','revenue','group','monthly','lookup','window']
