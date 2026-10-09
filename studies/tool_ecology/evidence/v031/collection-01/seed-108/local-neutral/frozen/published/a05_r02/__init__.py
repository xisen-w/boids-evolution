"""Native implementations of the six table service families."""
from statistics import mean, median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else None


def _fill(rows, policy):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = 0 if not vals else (sum(vals)/len(vals) if policy == 'mean' else median(vals) if policy == 'median' else 0)
    return [dict(r, units=(replacement if r.get('units') is None else r.get('units'))) for r in rows]


def _base(rows, request):
    out = _fill(rows, request.get('fill', 'zero'))
    for r in out:
        r['region'] = _region(r.get('region'))
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u*p
    return out


def clean(rows, lookup, request):
    out = _fill(rows, request.get('fill', 'zero'))
    for r in out: r['region'] = _region(r.get('region'))
    return out


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals)/len(vals) if vals else None
    return sum(vals)


def _group(rows, agg, monthly=False):
    groups = {}
    for r in rows:
        key = (r.get('date')[:7] if monthly and r.get('date') is not None else None, r.get('region')) if monthly else (r.get('region'),)
        if any(x is None for x in key): continue
        groups.setdefault(key, []).append(r.get('revenue_cents'))
    result=[]
    for key, vals in groups.items():
        item = ({'month':key[0], 'region':key[1]} if monthly else {'region':key[0]})
        item[agg+'_revenue_cents'] = _aggregate(vals, agg)
        result.append(item)
    result.sort(key=lambda x: tuple(str(x[k]) for k in (('month','region') if monthly else ('region',))))
    return result


def group(rows, lookup, request):
    return _group(_base(rows, request), request.get('agg','sum'))


def monthly(rows, lookup, request):
    return _group(_base(rows, request), request.get('agg','sum'), True)


def lookup(rows, lookup, request):
    out = _base(rows, request)
    targets = {_region(x.get('region')): x.get('target') for x in lookup}
    for r in out:
        target=targets.get(r.get('region'))
        rev=r['revenue_cents']
        r['revenue_cents_per_target'] = None if target in (None, 0) or rev is None else rev/target
    return out


def window(rows, lookup, request):
    out = _base(rows, request)
    width=request.get('window', 2)
    for i,r in enumerate(out):
        vals=[x['revenue_cents'] for x in out[max(0,i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals)/len(vals) if vals else None
    return out
