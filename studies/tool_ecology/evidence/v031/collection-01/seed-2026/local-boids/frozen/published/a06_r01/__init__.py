"""Native implementations of the six table service families."""
from statistics import mean, median


def _fill_units(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = 0 if not vals else (mean(vals) if method == 'mean' else median(vals) if method == 'median' else 0)
    return [dict(r, units=(replacement if r.get('units') is None else r.get('units'))) for r in rows]


def clean(rows, lookup, request):
    out = _fill_units(rows, request.get('fill', 'zero'))
    for r in out:
        v = r.get('region')
        r['region'] = v.strip().lower() if isinstance(v, str) else v
    return out


def _revenue(rows, request):
    out = _fill_units(rows, request.get('fill', 'zero'))
    for r in out:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _aggregate(vals, agg):
    if agg == 'count': return len(vals)
    if not vals: return 0 if agg == 'sum' else None
    return sum(vals) if agg == 'sum' else sum(vals) / len(vals)


def _groups(rows, keys, agg):
    buckets = {}
    for r in rows:
        vals = tuple(r.get(k) for k in keys)
        if any(v is None for v in vals): continue
        buckets.setdefault(vals, []).append(r.get('revenue_cents'))
    result=[]
    for vals, revenues in buckets.items():
        nonmissing=[v for v in revenues if v is not None]
        d=dict(zip(keys, vals)); d[agg+'_revenue_cents']=_aggregate(nonmissing, agg); result.append(d)
    result.sort(key=lambda d: tuple(str(d[k]) for k in keys))
    return result


def group(rows, lookup, request):
    data=_revenue(rows, request)
    for r in data:
        v=r.get('region'); r['region']=v.strip().lower() if isinstance(v,str) else v
    return _groups(data, ['region'], request.get('agg','sum'))


def monthly(rows, lookup, request):
    data=_revenue(rows, request)
    for r in data:
        v=r.get('region'); r['region']=v.strip().lower() if isinstance(v,str) else v
        d=r.get('date'); r['month']=d[:7] if d is not None else None
    return _groups(data, ['month','region'], request.get('agg','sum'))


def lookup(rows, lookup, request):
    data=_revenue(rows, request)
    targets={}
    for item in lookup:
        k=item.get('region')
        if isinstance(k,str): k=k.strip().lower()
        targets[k]=item.get('target')
    for r in data:
        k=r.get('region'); k=k.strip().lower() if isinstance(k,str) else k
        target=targets.get(k); rev=r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return data


def window(rows, lookup, request):
    data=_revenue(rows, request)
    width=request.get('window', 2)
    for i,r in enumerate(data):
        vals=[x['revenue_cents'] for x in data[max(0,i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return data
