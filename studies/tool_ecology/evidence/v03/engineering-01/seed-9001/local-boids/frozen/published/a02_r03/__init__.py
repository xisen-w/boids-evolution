"""Reusable, dependency-free row-table transformations."""
from statistics import median


def _fill(rows, request):
    result = [dict(r) for r in rows]
    vals = [r.get('units') for r in result if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero' or not vals:
        replacement = 0
    elif mode == 'mean':
        replacement = sum(vals) / len(vals)
    elif mode == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be zero, mean, or median")
    for r in result:
        if r.get('units') is None:
            r['units'] = replacement
    return result


def _revenue(rows, request, normalize=False):
    result = _fill(rows, request)
    for r in result:
        region = r.get('region')
        if normalize and isinstance(region, str):
            r['region'] = region.strip().lower()
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return result


def clean(rows, lookup, request):
    return _fill(rows, request) if not rows else _clean_nonempty(rows, request)


def _clean_nonempty(rows, request):
    result = _fill(rows, request)
    for r in result:
        v = r.get('region')
        if isinstance(v, str): r['region'] = v.strip().lower()
    return result


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _aggregate(values, agg):
    v = [x for x in values if x is not None]
    if agg == 'sum': return sum(v)
    if agg == 'count': return len(v)
    if agg == 'mean': return sum(v) / len(v) if v else None
    raise ValueError("agg must be sum, mean, or count")


def _group(rows, request, monthly=False):
    groups = {}
    for r in _revenue(rows, request, normalize=True):
        region = r.get('region')
        date = r.get('date')
        month = date[:7] if isinstance(date, str) else None
        if region is None or (monthly and month is None): continue
        key = (month, region) if monthly else region
        groups.setdefault(key, []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    keys = sorted(groups, key=lambda k: tuple(str(x) for x in k) if isinstance(k, tuple) else str(k))
    if monthly:
        return [{'month': k[0], 'region': k[1], f'{agg}_revenue_cents': _aggregate(groups[k], agg)} for k in keys]
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(groups[k], agg)} for k in keys]


def group(rows, lookup, request):
    return _group(rows, request)


def monthly(rows, lookup, request):
    return _group(rows, request, True)


def lookup(rows, lookup, request):
    result = _revenue(rows, request, normalize=True)
    targets = {}
    for x in lookup:
        k = x.get('region')
        if isinstance(k, str): k = k.strip().lower()
        targets[k] = x.get('target')
    for r in result:
        target, rev = targets.get(r.get('region')), r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return result


def window(rows, lookup, request):
    result = _revenue(rows, request)
    size = request.get('window', 2)
    if size not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    history = []
    for i, r in enumerate(result):
        history.append(r.get('revenue_cents'))
        vals = [x for x in history[max(0, i-size+1):i+1] if x is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return result
