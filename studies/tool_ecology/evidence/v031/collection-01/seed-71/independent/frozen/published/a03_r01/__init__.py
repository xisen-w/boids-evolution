"""Reusable row-table transforms for the six publication service families."""
from statistics import mean, median


def _copy(row):
    return dict(row)


def _units(rows, fill):
    present = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero' or not present:
        value = 0
    elif fill == 'mean':
        value = mean(present)
    elif fill == 'median':
        value = median(present)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [r.get('units') if r.get('units') is not None else value for r in rows]


def _base(rows, request):
    units = _units(rows, request.get('fill'))
    out = []
    for row, unit in zip(rows, units):
        d = _copy(row)
        region = d.get('region')
        d['region'] = region.strip().lower() if isinstance(region, str) else region
        d['units'] = unit
        price = d.get('price_cents')
        d['revenue_cents'] = unit * price if unit is not None and price is not None else None
        return_row = d
        out.append(return_row)
    return out


def clean(rows, lookup, request):
    units = _units(rows, request.get('fill'))
    out=[]
    for r,u in zip(rows,units):
        d=_copy(r); reg=d.get('region'); d['region']=reg.strip().lower() if isinstance(reg,str) else reg; d['units']=u; out.append(d)
    return out


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(vals, agg):
    vals=[v for v in vals if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    groups={}
    for r in _base(rows,request):
        key=r.get('region')
        if key is not None: groups.setdefault(key,[]).append(r['revenue_cents'])
    agg=request.get('agg'); name=agg+'_revenue_cents'
    return [{'region':k,name:_aggregate(v,agg)} for k,v in sorted(groups.items(),key=lambda x:str(x[0]))]


def monthly(rows, lookup, request):
    groups={}
    for r in _base(rows,request):
        month=r.get('date'); month=month[:7] if month is not None else None
        region=r.get('region')
        if month is not None and region is not None: groups.setdefault((month,region),[]).append(r['revenue_cents'])
    agg=request.get('agg'); name=agg+'_revenue_cents'
    keys=sorted(groups,key=lambda x:(str(x[0]),str(x[1])))
    return [{'month':m,'region':r,name:_aggregate(groups[(m,r)],agg)} for m,r in keys]


def lookup(rows, lookup, request):
    out=_base(rows,request)
    targets={}
    for item in lookup:
        key=item.get('region'); key=key.strip().lower() if isinstance(key,str) else key
        targets[key]=item.get('target')
    for r in out:
        target=targets.get(r.get('region')); rev=r.get('revenue_cents')
        r['revenue_cents_per_target']=rev/target if rev is not None and target is not None and target != 0 else None
    return out


def window(rows, lookup, request):
    out=_base(rows,request); width=request.get('window')
    if width not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out

__all__=['clean','revenue','group','monthly','lookup','window']
