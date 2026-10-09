"""Reusable row-oriented utilities for the publication service families."""
from copy import deepcopy
from statistics import mean, median


def _filled(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero' or not vals:
        replacement = 0
    elif mode == 'mean':
        replacement = mean(vals)
    elif mode == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be zero, mean, or median")
    return [replacement if r.get('units') is None else r.get('units') for r in rows]


def clean(rows, lookup, request):
    units = _filled(rows, request)
    out = []
    for row, unit in zip(rows, units):
        item = dict(row)
        item['region'] = row.get('region').strip().lower() if row.get('region') is not None else None
        item['units'] = unit
        out.append(item)
    return out


def revenue(rows, lookup, request):
    units = _filled(rows, request)
    out = []
    for row, unit in zip(rows, units):
        item = dict(row)
        item['units'] = unit
        price = row.get('price_cents')
        item['revenue_cents'] = None if unit is None or price is None else unit * price
        out.append(item)
    return out


def _normalized_region(row):
    value = row.get('region')
    return value.strip().lower() if value is not None else None


def _aggregate(values, agg):
    valid = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(valid) if valid else 0
    if agg == 'count':
        return len(valid)
    if agg == 'mean':
        return mean(valid) if valid else None
    raise ValueError("agg must be sum, mean, or count")


def _group(rows, request, monthly=False):
    data = revenue(rows, None, request)
    groups = {}
    for row in data:
        region = _normalized_region(row)
        month = row.get('date')[:7] if row.get('date') is not None else None
        if region is None or (monthly and month is None):
            continue
        key = (month, region) if monthly else (region,)
        groups.setdefault(key, []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    ordered = sorted(groups, key=lambda k: tuple(str(x) for x in k))
    result = []
    for key in ordered:
        value = _aggregate(groups[key], agg)
        if monthly:
            result.append({'month': key[0], 'region': key[1], f'{agg}_revenue_cents': value})
        else:
            result.append({'region': key[0], f'{agg}_revenue_cents': value})
    return result


def group(rows, lookup, request):
    return _group(rows, request, False)


def monthly(rows, lookup, request):
    return _group(rows, request, True)


def lookup(rows, lookup, request):
    data = revenue(rows, lookup, request)
    targets = {entry.get('region'): entry.get('target') for entry in (lookup or [])}
    out = []
    for original, item in zip(rows, data):
        region = _normalized_region(original)
        target = targets.get(region)
        value = item['revenue_cents']
        item['region'] = region
        item['revenue_cents_per_target'] = None if value is None or target is None or target == 0 else value / target
        out.append(item)
    return out


def window(rows, lookup, request):
    data = revenue(rows, lookup, request)
    width = request.get('window')
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    out = []
    values = []
    for i, item in enumerate(data):
        values.append(item['revenue_cents'])
        trailing = values[max(0, i-width+1):i+1]
        valid = [x for x in trailing if x is not None]
        item['roll_revenue_cents'] = mean(valid) if valid else None
        out.append(item)
    return out
