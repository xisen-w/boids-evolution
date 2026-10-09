"""Reusable row-oriented analytics services."""
from statistics import median


def _filled(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero' or not vals:
        value = 0
    elif mode == 'mean':
        value = sum(vals) / len(vals)
    elif mode == 'median':
        value = median(vals)
    else:
        raise ValueError("fill must be zero, mean, or median")
    out=[]
    for r in rows:
        x=dict(r)
        if x.get('units') is None: x['units']=value
        if x.get('region') is not None: x['region']=x['region'].strip().lower()
        out.append(x)
    return out


def _revenue(rows, request):
    out=_filled(rows, request)
    for r in out:
        u,p=r.get('units'),r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u*p
    return out


def clean(rows, lookup, request):
    return _filled(rows, request)


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _aggregate(values, agg):
    vals=[v for v in values if v is not None]
    if agg=='sum': return sum(vals)
    if agg=='count': return len(vals)
    if agg=='mean': return sum(vals)/len(vals) if vals else None
    raise ValueError('agg must be sum, mean, or count')


def _groups(entries, keys, agg):
    groups={}
    for key, val in entries: groups.setdefault(key, []).append(val)
    result=[]
    for key, vals in groups.items():
        row={k:v for k,v in zip(keys,key)}
        row[agg+'_revenue_cents']=_aggregate(vals,agg)
        result.append(row)
    result.sort(key=lambda row: tuple(str(row[k]) for k in keys))
    return result


def group(rows, lookup, request):
    data=_revenue(rows,request); agg=request.get('agg','sum')
    return _groups([((r['region'],),r['revenue_cents']) for r in data if r.get('region') is not None], ['region'], agg)


def monthly(rows, lookup, request):
    data=_revenue(rows,request); agg=request.get('agg','sum'); entries=[]
    for r in data:
        date=r.get('date'); month=date[:7] if date is not None else None
        if month is not None and r.get('region') is not None:
            entries.append(((month,r['region']),r['revenue_cents']))
    return _groups(entries,['month','region'],agg)


def lookup(rows, lookup, request):
    data=_revenue(rows,request)
    targets={}
    for item in lookup:
        region=item.get('region')
        if region is not None: targets[region.strip().lower()]=item.get('target')
    for r in data:
        target=targets.get(r.get('region'))
        val=r.get('revenue_cents')
        r['revenue_cents_per_target']=val/target if val is not None and target is not None and target != 0 else None
    return data


def window(rows, lookup, request):
    data=_revenue(rows,request); n=request.get('window',2)
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    vals=[]
    for i,r in enumerate(data):
        vals.append(r.get('revenue_cents'))
        recent=vals[max(0,i-n+1):i+1]
        valid=[x for x in recent if x is not None]
        r['roll_revenue_cents']=sum(valid)/len(valid) if valid else None
    return data
