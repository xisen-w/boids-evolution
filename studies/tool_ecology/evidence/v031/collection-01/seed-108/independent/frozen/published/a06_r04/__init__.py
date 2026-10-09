"""Dependency-free row table transforms."""
from statistics import mean, median


def _filled(rows, request):
    out = [dict(row) for row in rows]
    values = [r.get('units') for r in out if r.get('units') is not None]
    fill = request.get('fill', 'zero')
    replacement = mean(values) if fill == 'mean' and values else median(values) if fill == 'median' and values else 0
    for row in out:
        if row.get('units') is None:
            row['units'] = replacement
    return out


def clean(rows, lookup, request):
    out = _filled(rows, request)
    for row in out:
        if row.get('region') is not None:
            row['region'] = row['region'].strip().lower()
    return out


def _revenue(rows, request):
    out = _filled(rows, request)
    for row in out:
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return out


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _normalized_revenue(rows, request):
    out = _revenue(rows, request)
    for row in out:
        if row.get('region') is not None:
            row['region'] = row['region'].strip().lower()
    return out


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return mean(present) if present else None
    return sum(present)


def group(rows, lookup, request):
    groups = {}
    for row in _normalized_revenue(rows, request):
        key = row.get('region')
        if key is not None:
            groups.setdefault(key, []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': key, agg + '_revenue_cents': _aggregate(groups[key], agg)} for key in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    groups = {}
    for row in _normalized_revenue(rows, request):
        date, region = row.get('date'), row.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': r, agg + '_revenue_cents': _aggregate(groups[(m, r)], agg)}
            for m, r in sorted(groups, key=lambda pair: (str(pair[0]), str(pair[1])))]


def lookup(rows, lookup, request):
    data = _normalized_revenue(rows, request)
    targets = {}
    for entry in lookup:
        key = entry.get('region')
        if key is not None:
            targets[key.strip().lower()] = entry.get('target')
    for row in data:
        target, value = targets.get(row.get('region')), row['revenue_cents']
        row['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value / target
    return data


def window(rows, lookup, request):
    data = _revenue(rows, request)
    width = request.get('window', 2)
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for i, row in enumerate(data):
        values = [x['revenue_cents'] for x in data[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        row['roll_revenue_cents'] = mean(values) if values else None
    return data
