"""Reusable table services for the six publication workloads."""
from statistics import mean, median

_MISSING = object()

def _fill_units(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero':
        replacement = 0
    elif not vals:
        replacement = 0
    elif mode == 'mean':
        replacement = mean(vals)
    elif mode == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [replacement if r.get('units') is None else r.get('units') for r in rows]

def _base(rows, request):
    units = _fill_units(rows, request.get('fill', 'zero'))
    result = []
    for row, unit in zip(rows, units):
        out = dict(row)
        out['region'] = row.get('region').strip().lower() if isinstance(row.get('region'), str) else row.get('region')
        out['units'] = unit
        revenue = None if unit is None or row.get('price_cents') is None else unit * row['price_cents']
        out['revenue_cents'] = revenue
        result.append(out)
    return result

def clean(rows, lookup, request):
    """Normalize regions and fill units; preserve all other fields and row order."""
    units = _fill_units(rows, request.get('fill', 'zero'))
    result = []
    for row, unit in zip(rows, units):
        out = dict(row)
        out['region'] = row.get('region').strip().lower() if isinstance(row.get('region'), str) else row.get('region')
        out['units'] = unit
        result.append(out)
    return result

def revenue(rows, lookup, request):
    """Fill units, then append/derive revenue_cents."""
    return _base(rows, request)

def _aggregate(values, agg):
    valid = [v for v in values if v is not None]
    if agg == 'sum': return sum(valid)
    if agg == 'count': return len(valid)
    if agg == 'mean': return sum(valid) / len(valid) if valid else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")

def group(rows, lookup, request):
    data = _base(rows, request)
    groups = {}
    for row in data:
        key = row.get('region')
        if key is not None: groups.setdefault(key, []).append(row.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'region': key, f'{agg}_revenue_cents': _aggregate(groups[key], agg)} for key in sorted(groups, key=str)]

def monthly(rows, lookup, request):
    data = _base(rows, request)
    groups = {}
    for row in data:
        date, region = row.get('date'), row.get('region')
        month = date[:7] if isinstance(date, str) else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(row.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    keys = sorted(groups, key=lambda key: (str(key[0]), str(key[1])))
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(groups[(m,r)], agg)} for m,r in keys]

def lookup(rows, lookup, request):
    data = _base(rows, request)
    targets = {item.get('region'): item.get('target') for item in lookup}
    for row in data:
        target = targets.get(row.get('region'))
        revenue_value = row.get('revenue_cents')
        row['revenue_cents_per_target'] = None if target in (None, 0) or revenue_value is None else revenue_value / target
    return data

def window(rows, lookup, request):
    data = _base(rows, request)
    width = request.get('window', 2)
    if not isinstance(width, int) or width <= 0: raise ValueError('window must be a positive integer')
    for i, row in enumerate(data):
        vals = [r['revenue_cents'] for r in data[max(0, i-width+1):i+1] if r['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return data

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
