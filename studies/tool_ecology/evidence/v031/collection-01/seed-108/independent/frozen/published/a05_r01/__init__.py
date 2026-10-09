"""Native implementations of tabular service transformations."""
from statistics import median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _fill_units(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero':
        fill = 0
    elif not vals:
        fill = 0
    elif mode == 'mean':
        fill = sum(vals) / len(vals)
    elif mode == 'median':
        fill = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [fill if r.get('units') is None else r.get('units') for r in rows]


def _prepared(rows, request, normalize=True):
    units = _fill_units(rows, request.get('fill', 'zero'))
    result = []
    for row, unit in zip(rows, units):
        out = dict(row)
        if normalize:
            out['region'] = _region(row.get('region'))
        out['units'] = unit
        price = row.get('price_cents')
        out['revenue_cents'] = None if unit is None or price is None else unit * price
        result.append(out)
    return result


def clean(rows, lookup, request):
    units = _fill_units(rows, request.get('fill', 'zero'))
    out=[]
    for row, unit in zip(rows, units):
        item=dict(row); item['region']=_region(row.get('region')); item['units']=unit; out.append(item)
    return out


def revenue(rows, lookup, request):
    return _prepared(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum': return sum(present)
    if agg == 'count': return len(present)
    if agg == 'mean': return sum(present)/len(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    groups={}
    for row in _prepared(rows, request):
        key=row.get('region')
        if key is not None: groups.setdefault(key, []).append(row.get('revenue_cents'))
    agg=request.get('agg','sum')
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    groups={}
    for row in _prepared(rows, request):
        month=row.get('date')
        month=month[:7] if month is not None else None
        region=row.get('region')
        if month is not None and region is not None:
            groups.setdefault((month,region), []).append(row.get('revenue_cents'))
    agg=request.get('agg','sum')
    keys=sorted(groups, key=lambda k:(str(k[0]),str(k[1])))
    return [{'month':m,'region':r,f'{agg}_revenue_cents':_aggregate(groups[(m,r)],agg)} for m,r in keys]


def lookup(rows, lookup, request):
    out=_prepared(rows, request)
    targets={_region(item.get('region')):item.get('target') for item in lookup if item.get('region') is not None}
    for row in out:
        target=targets.get(row.get('region'))
        revenue_value=row.get('revenue_cents')
        row['revenue_cents_per_target'] = None if target is None or target == 0 or revenue_value is None else revenue_value/target
    return out


def window(rows, lookup, request):
    out=_prepared(rows, request)
    n=request.get('window')
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    vals=[]
    for i,row in enumerate(out):
        vals.append(row.get('revenue_cents'))
        segment=[v for v in vals[max(0,i-n+1):i+1] if v is not None]
        row['roll_revenue_cents']=sum(segment)/len(segment) if segment else None
    return out
