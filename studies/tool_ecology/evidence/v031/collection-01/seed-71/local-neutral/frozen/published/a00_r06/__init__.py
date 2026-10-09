"""Small, dependency-free services for row-oriented sales tables."""
from statistics import mean, median


def _base(rows, request):
    fill = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = {'zero': 0, 'mean': (mean(vals) if vals else 0), 'median': (median(vals) if vals else 0)}.get(fill, 0)
    result = []
    for row in rows:
        r = dict(row)
        region = r.get('region')
        r['region'] = region.strip().lower() if isinstance(region, str) else region
        if r.get('units') is None:
            r['units'] = replacement
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = u * p if u is not None and p is not None else None
        result.append(r)
    return result


def clean(rows, lookup, request):
    fill = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = {'zero': 0, 'mean': (mean(vals) if vals else 0), 'median': (median(vals) if vals else 0)}.get(fill, 0)
    result = []
    for row in rows:
        r = dict(row)
        region = r.get('region')
        r['region'] = region.strip().lower() if isinstance(region, str) else region
        if r.get('units') is None:
            r['units'] = replacement
        result.append(r)
    return result


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(values, agg):
    xs = [v for v in values if v is not None]
    if agg == 'count': return len(xs)
    if agg == 'mean': return sum(xs) / len(xs) if xs else None
    return sum(xs)


def group(rows, lookup, request):
    groups = {}
    for r in _base(rows, request):
        key = r['region']
        if key is not None: groups.setdefault(key, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': k, agg + '_revenue_cents': _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    groups = {}
    for r in _base(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is None or region is None: continue
        groups.setdefault((month, region), []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': reg, agg + '_revenue_cents': _aggregate(groups[(m, reg)], agg)}
            for m, reg in sorted(groups, key=lambda x: (str(x[0]), str(x[1])))]


def lookup_service(rows, lookup, request):
    out = _base(rows, request)
    targets = {r.get('region'): r.get('target') for r in lookup}
    for r in out:
        target = targets.get(r.get('region'))
        rev = r.get('revenue_cents')
        r['revenue_cents_per_target'] = rev / target if target not in (None, 0) and rev is not None else None
    return out


def window(rows, lookup, request):
    out = _base(rows, request)
    width = request.get('window', 2)
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
