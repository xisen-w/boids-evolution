"""Small, dependency-free implementations of the tabular service families."""
from collections import defaultdict
from statistics import mean, median


def _filled(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill')
    if mode == 'zero':
        replacement = 0
    elif mode == 'mean':
        replacement = mean(vals) if vals else 0
    elif mode == 'median':
        replacement = median(vals) if vals else 0
    else:
        raise ValueError("request.fill must be 'zero', 'mean', or 'median'")
    out=[]
    for row in rows:
        d=dict(row)
        if d.get('units') is None: d['units']=replacement
        out.append(d)
    return out


def _prepare(rows, request, normalize=True):
    out=[]
    for d in _filled(rows, request):
        if normalize:
            region=d.get('region')
            d['region']=region.strip().lower() if isinstance(region, str) else region
        u,p=d.get('units'),d.get('price_cents')
        d['revenue_cents']=u*p if u is not None and p is not None else None
        out.append(d)
    return out


def clean(rows, lookup, request):
    out=_filled(rows, request)
    for d in out:
        region=d.get('region')
        d['region']=region.strip().lower() if isinstance(region,str) else region
    return out


def revenue(rows, lookup, request):
    return _prepare(rows, request, normalize=False)


def _aggregate(values, agg):
    values=[v for v in values if v is not None]
    if agg == 'sum': return sum(values)
    if agg == 'count': return len(values)
    if agg == 'mean': return mean(values) if values else None
    raise ValueError("request.agg must be 'sum', 'mean', or 'count'")


def _groups(rows, request, monthly=False):
    agg=request.get('agg')
    if agg not in ('sum','mean','count'): raise ValueError("invalid request.agg")
    bins=defaultdict(list)
    for d in _prepare(rows, request):
        region=d.get('region')
        month=(d.get('date')[:7] if d.get('date') is not None else None) if monthly else None
        if region is None or (monthly and month is None): continue
        key=(month,region) if monthly else region
        bins[key].append(d.get('revenue_cents'))
    def sk(k): return tuple(str(x) for x in k) if isinstance(k,tuple) else str(k)
    result=[]
    for key in sorted(bins,key=sk):
        value=_aggregate(bins[key],agg)
        item={'region':key[1] if monthly else key, f'{agg}_revenue_cents':value}
        if monthly: item={'month':key[0], **item}
        result.append(item)
    return result


def group(rows, lookup, request):
    return _groups(rows,request)


def monthly(rows, lookup, request):
    return _groups(rows,request,True)


def lookup(rows, lookup, request):
    out=_prepare(rows,request)
    targets={r.get('region'):r.get('target') for r in lookup}
    for d in out:
        target=targets.get(d.get('region'))
        rev=d.get('revenue_cents')
        d['revenue_cents_per_target']=rev/target if rev is not None and target not in (None,0) else None
    return out


def window(rows, lookup, request):
    out=_prepare(rows,request, normalize=False)
    n=request.get('window')
    if n not in (2,3,4): raise ValueError('request.window must be 2, 3, or 4')
    for i,d in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        d['roll_revenue_cents']=mean(vals) if vals else None
    return out

__all__=['clean','revenue','group','monthly','lookup','window']
