"""Small, dependency-free dataframe-style services for list-of-dict tables."""
from statistics import median


def _filled(rows, request):
    """Copy rows and fill missing units; never mutate caller data."""
    out = [dict(r) for r in rows]
    missing = [i for i, r in enumerate(out) if r.get('units') is None]
    if not missing:
        return out
    vals = [r.get('units') for r in out if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    value = (0 if not vals else (sum(vals)/len(vals) if mode == 'mean' else median(vals))) if mode in ('mean','median') else 0
    for i in missing:
        out[i]['units'] = value
    return out


def _norm(region):
    return region.strip().lower() if isinstance(region, str) else region


def clean(rows, lookup, request):
    out = _filled(rows, request)
    for r in out:
        r['region'] = _norm(r.get('region'))
    return out


def revenue(rows, lookup, request):
    out = _filled(rows, request)
    for r in out:
        r['revenue_cents'] = None if r.get('units') is None or r.get('price_cents') is None else r['units'] * r['price_cents']
    return out


def _agg(vals, agg):
    if agg == 'count':
        return len(vals)
    if not vals:
        return 0 if agg == 'sum' else None
    return sum(vals) if agg == 'sum' else sum(vals) / len(vals)


def _aggregate(groups, keys, agg):
    result=[]
    for key, vals in groups.items():
        row = dict(zip(keys, key))
        row[agg + '_revenue_cents'] = _agg(vals, agg)
        result.append(row)
    result.sort(key=lambda r: tuple(str(r[k]) for k in keys))
    return result


def group(rows, lookup, request):
    base = revenue(rows, lookup, request)
    agg = request.get('agg', 'sum')
    groups={}
    for r in base:
        region = _norm(r.get('region'))
        val = r.get('revenue_cents')
        if region is None:
            continue
        groups.setdefault((region,), []).append(val) if val is not None else groups.setdefault((region,), [])
    return _aggregate(groups, ('region',), agg)


def monthly(rows, lookup, request):
    base = revenue(rows, lookup, request)
    agg = request.get('agg', 'sum')
    groups={}
    for r in base:
        region = _norm(r.get('region'))
        date = r.get('date')
        month = date[:7] if date is not None else None
        if region is None or month is None:
            continue
        vals = groups.setdefault((month, region), [])
        if r.get('revenue_cents') is not None:
            vals.append(r['revenue_cents'])
    return _aggregate(groups, ('month','region'), agg)


def lookup(rows, lookup, request):
    out = revenue(rows, lookup, request)
    targets = {_norm(x.get('region')): x.get('target') for x in lookup}
    for r in out:
        region = _norm(r.get('region'))
        target = targets.get(region)
        rev = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if region is None or target is None or target == 0 or rev is None else rev / target
    return out


def window(rows, lookup, request):
    out = revenue(rows, lookup, request)
    width = request.get('window', 2)
    values=[]
    for i, r in enumerate(out):
        values.append(r.get('revenue_cents'))
        recent = [v for v in values[max(0, i-width+1):i+1] if v is not None]
        r['roll_revenue_cents'] = sum(recent)/len(recent) if recent else None
    return out
