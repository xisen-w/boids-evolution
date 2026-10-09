"""Tabular data service adapters."""
from statistics import mean, median


def _filled(rows, request):
    out = [dict(r) for r in rows]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    replacement = (mean(vals) if mode == 'mean' else median(vals) if mode == 'median' else 0) if vals else 0
    for r in out:
        if r.get('units') is None:
            r['units'] = replacement
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    out = [dict(r) for r in rows]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    replacement = (mean(vals) if mode == 'mean' else median(vals) if mode == 'median' else 0) if vals else 0
    for r in out:
        if isinstance(r.get('region'), str): r['region'] = r['region'].strip().lower()
        if r.get('units') is None: r['units'] = replacement
    return out


def revenue(rows, lookup, request):
    return _filled(rows, request)


def _norm(value):
    return value.strip().lower() if isinstance(value, str) else value


def _prepared(rows, request):
    out = _filled(rows, request)
    for r in out:
        if isinstance(r.get('region'), str): r['region'] = _norm(r['region'])
    return out


def _aggregate(vals, agg):
    vals = [v for v in vals if v is not None]
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals) / len(vals) if vals else None
    return sum(vals)


def group(rows, lookup, request):
    groups = {}
    for r in _prepared(rows, request):
        key = r.get('region')
        if key is not None: groups.setdefault(key, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    groups = {}
    for r in _prepared(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None: groups.setdefault((month, region), []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(groups[(m, r)], agg)}
            for m, r in sorted(groups, key=lambda k: (str(k[0]), str(k[1])))]


def lookup(rows, lookup, request):
    out = _prepared(rows, request)
    targets = {_norm(x.get('region')): x.get('target') for x in lookup}
    for r in out:
        t, v = targets.get(r.get('region')), r['revenue_cents']
        r['revenue_cents_per_target'] = v / t if v is not None and t not in (None, 0) else None
    return out


def window(rows, lookup, request):
    out = _filled(rows, request)
    width = request.get('window', 2)
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
