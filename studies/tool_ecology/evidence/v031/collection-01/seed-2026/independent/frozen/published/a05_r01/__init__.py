"""Reusable native-Python table transforms for sales service families."""
from statistics import median


def _fill_units(rows, method):
    values = [r.get('units') for r in rows if r.get('units') is not None]
    fill = 0 if not values else (sum(values) / len(values) if method == 'mean' else median(values) if method == 'median' else 0)
    return [dict(r, units=(fill if r.get('units') is None else r.get('units'))) for r in rows]


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _base(rows, request):
    result = []
    for row in _fill_units(rows, request.get('fill', 'zero')):
        item = dict(row)
        item['region'] = _region(item.get('region'))
        u, p = item.get('units'), item.get('price_cents')
        item['revenue_cents'] = None if u is None or p is None else u * p
        result.append(item)
    return result


def clean(rows, lookup, request):
    return [dict(r, region=_region(r.get('region'))) for r in _fill_units(rows, request.get('fill', 'zero'))]


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(values, agg):
    values = [v for v in values if v is not None]
    if agg == 'count': return len(values)
    if agg == 'mean': return sum(values) / len(values) if values else None
    return sum(values)


def group(rows, lookup, request):
    groups = {}
    for row in _base(rows, request):
        key = row.get('region')
        if key is not None: groups.setdefault(key, []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(v, agg)} for k, v in sorted(groups.items(), key=lambda p: str(p[0]))]


def monthly(rows, lookup, request):
    groups = {}
    for row in _base(rows, request):
        date, region = row.get('date'), row.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None: groups.setdefault((month, region), []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(v, agg)}
            for (m, r), v in sorted(groups.items(), key=lambda p: (str(p[0][0]), str(p[0][1])))]


def lookup(rows, lookup, request):
    result = _base(rows, request)
    targets = {_region(x.get('region')): x.get('target') for x in lookup}
    for row in result:
        target, value = targets.get(row.get('region')), row['revenue_cents']
        row['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value / target
    return result


def window(rows, lookup, request):
    result = _base(rows, request)
    width = request.get('window', 2)
    for i, row in enumerate(result):
        vals = [r['revenue_cents'] for r in result[max(0, i-width+1):i+1] if r['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return result
