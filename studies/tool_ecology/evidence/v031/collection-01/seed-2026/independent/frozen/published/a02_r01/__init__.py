"""Reusable services for the tabular publication tasks."""
from statistics import mean, median


def _normalized(value):
    return value.strip().lower() if isinstance(value, str) else value


def _prepare(rows, request):
    """Copy rows, normalize region, fill missing units, derive revenue."""
    result = [dict(row) for row in rows]
    for row in result:
        row['region'] = _normalized(row.get('region'))
    missing = [r.get('units') for r in result if r.get('units') is not None]
    fill = request.get('fill', 'zero')
    if not missing:
        replacement = 0
    elif fill == 'mean':
        replacement = mean(missing)
    elif fill == 'median':
        replacement = median(missing)
    else:
        replacement = 0
    for row in result:
        if row.get('units') is None:
            row['units'] = replacement
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return result


def clean(rows, lookup, request):
    """Normalize region and fill units, preserving all other data and order."""
    result = [dict(row) for row in rows]
    for row in result:
        row['region'] = _normalized(row.get('region'))
    vals = [r.get('units') for r in result if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    replacement = (mean(vals) if mode == 'mean' else median(vals) if mode == 'median' else 0) if vals else 0
    for row in result:
        if row.get('units') is None:
            row['units'] = replacement
    return result


def revenue(rows, lookup, request):
    return _prepare(rows, request)


def _aggregate(values, agg):
    values = [v for v in values if v is not None]
    if agg == 'count':
        return len(values)
    if agg == 'mean':
        return sum(values) / len(values) if values else None
    return sum(values)


def group(rows, lookup, request):
    groups = {}
    for row in _prepare(rows, request):
        key = row.get('region')
        if key is not None:
            groups.setdefault(key, []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': key, f'{agg}_revenue_cents': _aggregate(groups[key], agg)}
            for key in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    groups = {}
    for row in _prepare(rows, request):
        date, region = row.get('date'), row.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    keys = sorted(groups, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(groups[(m, r)], agg)} for m, r in keys]


def lookup(rows, lookup, request):
    result = _prepare(rows, request)
    targets = {_normalized(entry.get('region')): entry.get('target') for entry in lookup}
    for row in result:
        target = targets.get(row.get('region'))
        value = row['revenue_cents']
        row['revenue_cents_per_target'] = value / target if value is not None and target not in (None, 0) else None
    return result


def window(rows, lookup, request):
    result = _prepare(rows, request)
    width = request.get('window', 2)
    for i, row in enumerate(result):
        vals = [r['revenue_cents'] for r in result[max(0, i-width+1):i+1] if r['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return result
