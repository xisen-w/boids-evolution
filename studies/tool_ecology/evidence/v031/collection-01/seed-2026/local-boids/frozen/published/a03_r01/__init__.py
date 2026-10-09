"""Reusable implementations of the six table service families."""
from statistics import median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _filled(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero' or not vals:
        fill = 0
    elif mode == 'mean':
        fill = sum(vals) / len(vals)
    elif mode == 'median':
        fill = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [fill if r.get('units') is None else r.get('units') for r in rows]


def _base(rows, request):
    units = _filled(rows, request.get('fill'))
    result = []
    for row, unit in zip(rows, units):
        r = dict(row)
        r['region'] = _region(row.get('region'))
        r['units'] = unit
        revenue = None if unit is None or row.get('price_cents') is None else unit * row['price_cents']
        r['revenue_cents'] = revenue
        result.append(r)
    return result


def clean(rows, lookup, request):
    units = _filled(rows, request.get('fill'))
    out=[]
    for row, unit in zip(rows, units):
        r=dict(row); r['region']=_region(row.get('region')); r['units']=unit; out.append(r)
    return out


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(groups, agg, keys):
    if agg not in ('sum','mean','count'):
        raise ValueError("agg must be 'sum', 'mean', or 'count'")
    out=[]
    for key, vals in groups.items():
        vals=[v for v in vals if v is not None]
        if agg == 'sum': value=sum(vals)
        elif agg == 'count': value=len(vals)
        else: value=(sum(vals)/len(vals)) if vals else None
        if agg in ('sum','count') and not vals: value=0
        row=dict(zip(keys,key)); row[agg+'_revenue_cents']=value; out.append(row)
    out.sort(key=lambda r: tuple(str(r[k]) for k in keys))
    return out


def group(rows, lookup, request):
    groups={}
    for r in _base(rows,request):
        key=r['region']
        if key is not None: groups.setdefault((key,),[]).append(r['revenue_cents'])
    return _aggregate(groups, request.get('agg'), ('region',))


def monthly(rows, lookup, request):
    groups={}
    for r in _base(rows,request):
        date=r.get('date'); month=date[:7] if date is not None else None
        if month is not None and r['region'] is not None:
            groups.setdefault((month,r['region']),[]).append(r['revenue_cents'])
    return _aggregate(groups,request.get('agg'),('month','region'))


def lookup_rate(rows, lookup, request):
    out=_base(rows,request)
    targets={_region(x.get('region')): x.get('target') for x in lookup}
    for r in out:
        target=targets.get(r['region'])
        val=r['revenue_cents']
        r['revenue_cents_per_target'] = None if target is None or target == 0 or val is None else val/target
    return out


def window(rows, lookup, request):
    out=_base(rows,request)
    width=request.get('window')
    if width not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out


# Public adapter names used by publish.json.
lookup_service = lookup_rate
