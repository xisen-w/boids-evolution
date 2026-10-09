"""Reusable implementations of the recurring tabular services."""
from collections import defaultdict
from statistics import mean, median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _filled(rows, request):
    fill = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero' or not vals:
        replacement = 0
    elif fill == 'mean':
        replacement = mean(vals)
    elif fill == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out=[]
    for row in rows:
        item=dict(row)
        if item.get('units') is None:
            item['units']=replacement
        out.append(item)
    return out


def _base(rows, request):
    out=[]
    for item in _filled(rows, request):
        item['region'] = _region(item.get('region'))
        u,p=item.get('units'),item.get('price_cents')
        item['revenue_cents'] = None if u is None or p is None else u*p
        out.append(item)
    return out


def clean(rows, lookup, request):
    return [{**r, 'region': _region(r.get('region'))} for r in _filled(rows, request)]


def revenue(rows, lookup, request):
    out=[]
    for item in _filled(rows, request):
        u,p=item.get('units'),item.get('price_cents')
        item['revenue_cents'] = None if u is None or p is None else u*p
        out.append(item)
    return out


def _aggregate(values, agg):
    vals=[v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    agg=request.get('agg','sum'); groups=defaultdict(list)
    for r in _base(rows, request):
        if r.get('region') is not None: groups[r['region']].append(r['revenue_cents'])
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(v,agg)} for k,v in sorted(groups.items(), key=lambda x:str(x[0]))]


def monthly(rows, lookup, request):
    agg=request.get('agg','sum'); groups=defaultdict(list)
    for r in _base(rows, request):
        date=r.get('date'); month=date[:7] if date is not None else None
        region=r.get('region')
        if month is not None and region is not None: groups[(month,region)].append(r['revenue_cents'])
    keys=sorted(groups, key=lambda k:(str(k[0]),str(k[1])))
    return [{'month':m,'region':reg,f'{agg}_revenue_cents':_aggregate(groups[(m,reg)],agg)} for m,reg in keys]


def lookup(rows, lookup, request):
    targets={_region(x.get('region')):x.get('target') for x in lookup}
    out=_base(rows, request)
    for r in out:
        target=targets.get(r.get('region')); revenue_value=r['revenue_cents']
        r['revenue_cents_per_target'] = None if target in (None,0) or revenue_value is None else revenue_value/target
    return out


def window(rows, lookup, request):
    w=request.get('window')
    if w not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    out=revenue(rows, lookup, request)
    for i,r in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-w+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out
