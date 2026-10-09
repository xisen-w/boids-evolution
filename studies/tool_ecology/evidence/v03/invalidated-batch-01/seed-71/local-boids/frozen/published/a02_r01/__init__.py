"""Reusable row-table service transformations."""
from statistics import mean, median


def _base(rows, request):
    fill = request.get('fill', 'zero')
    present = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero' or not present:
        replacement = 0
    elif fill == 'mean':
        replacement = mean(present)
    elif fill == 'median':
        replacement = median(present)
    else:
        raise ValueError("fill must be zero, mean, or median")
    out=[]
    for source in rows:
        row=dict(source)
        if row.get('units') is None:
            row['units']=replacement
        region=row.get('region')
        row['region']=None if region is None else region.strip().lower()
        u,p=row.get('units'),row.get('price_cents')
        row['revenue_cents']=None if u is None or p is None else u*p
        out.append(row)
    return out


def clean(rows, lookup, request):
    result = _base(rows, request)
    for source, row in zip(rows, result):
        if 'revenue_cents' in source:
            row['revenue_cents'] = source['revenue_cents']
        else:
            row.pop('revenue_cents', None)
    return result


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(rows, agg):
    vals=[r['revenue_cents'] for r in rows if r['revenue_cents'] is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("agg must be sum, mean, or count")


def group(rows, lookup, request):
    buckets={}
    for r in _base(rows,request):
        key=r.get('region')
        if key is not None: buckets.setdefault(key,[]).append(r)
    agg=request.get('agg','sum')
    return [{'region':k, agg+'_revenue_cents':_aggregate(buckets[k],agg)}
            for k in sorted(buckets,key=str)]


def monthly(rows, lookup, request):
    buckets={}
    for r in _base(rows,request):
        date=r.get('date'); month=date[:7] if date is not None else None
        region=r.get('region')
        if month is not None and region is not None:
            buckets.setdefault((month,region),[]).append(r)
    agg=request.get('agg','sum')
    return [{'month':m,'region':r,agg+'_revenue_cents':_aggregate(buckets[(m,r)],agg)}
            for m,r in sorted(buckets,key=lambda x:(str(x[0]),str(x[1])))]


def lookup(rows, lookup, request):
    result=_base(rows,request)
    targets={}
    for item in lookup:
        reg=item.get('region')
        key=None if reg is None else reg.strip().lower()
        targets[key]=item.get('target')
    for row in result:
        target=targets.get(row.get('region'))
        revenue=row['revenue_cents']
        row['revenue_cents_per_target']=(None if target is None or target==0 or revenue is None else revenue/target)
    return result


def window(rows, lookup, request):
    result=_base(rows,request)
    width=request.get('window',2)
    if width not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    vals=[]
    for i,row in enumerate(result):
        vals.append(row['revenue_cents'])
        recent=[x for x in vals[max(0,i-width+1):] if x is not None]
        row['roll_revenue_cents']=sum(recent)/len(recent) if recent else None
    return result

__all__=['clean','revenue','group','monthly','lookup','window']
