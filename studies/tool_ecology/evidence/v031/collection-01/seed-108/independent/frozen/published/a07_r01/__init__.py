"""Native implementations of the tabular service families."""
from copy import copy
from statistics import mean, median


def _number(value):
    return value is not None


def _prepared(rows, request):
    """Copy rows, normalize regions, fill units, and append revenue."""
    fill = request.get('fill', 'zero')
    units = [row.get('units') for row in rows if row.get('units') is not None]
    if fill == 'zero':
        replacement = 0
    elif fill == 'mean':
        replacement = mean(units) if units else 0
    elif fill == 'median':
        replacement = median(units) if units else 0
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    result = []
    for source in rows:
        row = dict(source)
        if row.get('region') is not None:
            row['region'] = row['region'].strip().lower()
        if row.get('units') is None:
            row['units'] = replacement
        u, p = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if u is None or p is None else u * p
        result.append(row)
    return result


def clean(rows, lookup, request):
    fill = request.get('fill', 'zero')
    units = [row.get('units') for row in rows if row.get('units') is not None]
    if fill == 'zero':
        replacement = 0
    elif fill == 'mean':
        replacement = mean(units) if units else 0
    elif fill == 'median':
        replacement = median(units) if units else 0
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    result = []
    for source in rows:
        row = dict(source)
        if row.get('region') is not None:
            row['region'] = row['region'].strip().lower()
        if row.get('units') is None:
            row['units'] = replacement
        result.append(row)
    return result


def revenue(rows, lookup, request):
    return _prepared(rows, request)


def _aggregate(values, agg):
    valid = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(valid) if valid else 0
    if agg == 'count':
        return len(valid)
    if agg == 'mean':
        return mean(valid) if valid else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    prepared = _prepared(rows, request)
    agg = request.get('agg', 'sum')
    buckets = {}
    for row in prepared:
        key = row.get('region')
        if key is not None:
            buckets.setdefault(key, []).append(row['revenue_cents'])
    return [{'region': key, f'{agg}_revenue_cents': _aggregate(buckets[key], agg)}
            for key in sorted(buckets, key=str)]


def monthly(rows, lookup, request):
    prepared = _prepared(rows, request)
    agg = request.get('agg', 'sum')
    buckets = {}
    for row in prepared:
        region = row.get('region')
        date = row.get('date')
        month = date[:7] if date is not None else None
        if region is not None and month is not None:
            buckets.setdefault((month, region), []).append(row['revenue_cents'])
    return [{'month': month, 'region': region,
             f'{agg}_revenue_cents': _aggregate(buckets[(month, region)], agg)}
            for month, region in sorted(buckets, key=lambda pair: (str(pair[0]), str(pair[1])))]


def lookup(rows, lookup, request):
    prepared = _prepared(rows, request)
    targets = {entry.get('region'): entry.get('target') for entry in lookup}
    for row in prepared:
        target = targets.get(row.get('region'))
        value = row['revenue_cents']
        row['revenue_cents_per_target'] = (None if target is None or target == 0 or value is None
                                           else value / target)
    return prepared


def window(rows, lookup, request):
    prepared = _prepared(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for index, row in enumerate(prepared):
        values = [item['revenue_cents'] for item in prepared[max(0, index-width+1):index+1]
                  if item['revenue_cents'] is not None]
        row['roll_revenue_cents'] = mean(values) if values else None
    return prepared
