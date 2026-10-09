"""Small, non-mutating tabular service transforms."""
from statistics import mean, median


def _norm(value):
    return value.strip().lower() if isinstance(value, str) else value


def _fill_units(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = 0 if not vals else (sum(vals)/len(vals) if mode == 'mean' else median(vals) if mode == 'median' else 0)
    return [replacement if r.get('units') is None else r.get('units') for r in rows]


def clean(rows, lookup, request):
    units = _fill_units(rows, request.get('fill'))
    return [dict(r, region=_norm(r.get('region')), units=u) for r,u in zip(rows, units)]


def revenue(rows, lookup, request):
    base = clean(rows, lookup, request)
    for r in base:
        u,p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u*p
    return base


def _aggregate(values, agg):
    v = [x for x in values if x is not None]
    if agg == 'count': return len(v)
    if agg == 'mean': return sum(v)/len(v) if v else None
    return sum(v) if v else 0


def group(rows, lookup, request):
    data = revenue(rows, lookup, request)
    groups = {}
    for r in data:
        key = r.get('region')
        if key is not None: groups.setdefault(key, []).append(r['revenue_cents'])
    agg=request.get('agg','sum')
    return [{'region':k, f'{agg}_revenue_cents':_aggregate(v,agg)} for k,v in sorted(groups.items(),key=lambda x:str(x[0]))]


def monthly(rows, lookup, request):
    data = revenue(rows, lookup, request)
    groups={}
    for r in data:
        date, region = r.get('date'), r.get('region')
        month=date[:7] if date is not None else None
        if month is not None and region is not None: groups.setdefault((month,region),[]).append(r['revenue_cents'])
    agg=request.get('agg','sum')
    return [{'month':m,'region':r,f'{agg}_revenue_cents':_aggregate(v,agg)} for (m,r),v in sorted(groups.items(),key=lambda x:(str(x[0][0]),str(x[0][1])))]


def lookup_service(rows, lookup, request):
    data=revenue(rows,lookup,request)
    targets={_norm(x.get('region')):x.get('target') for x in lookup}
    for r in data:
        target=targets.get(r.get('region'))
        value=r.get('revenue_cents')
        r['revenue_cents_per_target']=None if target is None or target == 0 or value is None else value/target
    return data


def window(rows, lookup, request):
    data=revenue(rows,lookup,request)
    n=request.get('window',2)
    for i,r in enumerate(data):
        vals=[x['revenue_cents'] for x in data[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return data
