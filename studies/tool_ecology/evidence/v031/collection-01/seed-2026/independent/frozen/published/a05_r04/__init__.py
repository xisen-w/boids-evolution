"""Native Python sales-table service adapters with input-preserving transforms."""
from statistics import median


def _fill(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if not vals:
        value = 0
    elif method == 'mean':
        value = sum(vals) / len(vals)
    elif method == 'median':
        value = median(vals)
    else:
        value = 0
    return [dict(row, units=value if row.get('units') is None else row.get('units')) for row in rows]


def _revenue(rows, request):
    result = _fill(rows, request.get('fill', 'zero'))
    for row in result:
        u, p = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if u is None or p is None else u * p
    return result


def _norm(v):
    return v.strip().lower() if isinstance(v, str) else v


def clean(rows, lookup, request):
    return [dict(row, region=_norm(row.get('region'))) for row in _fill(rows, request.get('fill', 'zero'))]


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _normalized_revenue(rows, request):
    result = _revenue(rows, request)
    for r in result:
        r['region'] = _norm(r.get('region'))
    return result


def _agg(values, agg):
    values = [v for v in values if v is not None]
    if agg == 'count':
        return len(values)
    if agg == 'mean':
        return sum(values) / len(values) if values else None
    return sum(values)


def group(rows, lookup, request):
    groups = {}
    for row in _normalized_revenue(rows, request):
        key = row.get('region')
        if key is not None:
            groups.setdefault(key, []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': key, f'{agg}_revenue_cents': _agg(vals, agg)} for key, vals in sorted(groups.items(), key=lambda x: str(x[0]))]


def monthly(rows, lookup, request):
    groups = {}
    for row in _normalized_revenue(rows, request):
        date, region = row.get('date'), row.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    keys = sorted(groups, key=lambda x: (str(x[0]), str(x[1])))
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _agg(groups[(m, r)], agg)} for m, r in keys]


def lookup(rows, lookup, request):
    result = _normalized_revenue(rows, request)
    targets = {_norm(item.get('region')): item.get('target') for item in lookup}
    for row in result:
        target, value = targets.get(row.get('region')), row['revenue_cents']
        row['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value / target
    return result


def window(rows, lookup, request):
    result = _revenue(rows, request)
    width = request.get('window', 2)
    for i, row in enumerate(result):
        vals = [r['revenue_cents'] for r in result[max(0, i-width+1):i+1] if r['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return result
