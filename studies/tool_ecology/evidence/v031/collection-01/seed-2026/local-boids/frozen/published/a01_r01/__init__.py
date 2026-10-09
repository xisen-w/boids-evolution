"""Small, dependency-free adapters for tabular service families."""
from statistics import median


def _fill(rows, request):
    method = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if method == 'zero' or not vals:
        replacement = 0
    elif method == 'mean':
        replacement = sum(vals) / len(vals)
    elif method == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be zero, mean, or median")
    return [replacement if r.get('units') is None else r.get('units') for r in rows]


def _region(row):
    value = row.get('region')
    return value.strip().lower() if isinstance(value, str) else value


def _revenue(rows, request):
    units = _fill(rows, request)
    out = []
    for row, unit in zip(rows, units):
        item = dict(row)
        item['region'] = _region(row)
        price = row.get('price_cents')
        item['revenue_cents'] = None if unit is None or price is None else unit * price
        out.append(item)
    return out


def clean(rows, lookup, request):
    units = _fill(rows, request)
    return [{**row, 'region': _region(row), 'units': unit} for row, unit in zip(rows, units)]


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum': return sum(present)
    if agg == 'count': return len(present)
    if agg == 'mean': return sum(present) / len(present) if present else None
    raise ValueError('agg must be sum, mean, or count')


def group(rows, lookup, request):
    groups = {}
    for row in _revenue(rows, request):
        key = row.get('region')
        if key is not None: groups.setdefault(key, []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': key, agg + '_revenue_cents': _aggregate(groups[key], agg)}
            for key in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    groups = {}
    for row in _revenue(rows, request):
        date, region = row.get('date'), row.get('region')
        if date is None or region is None: continue
        key = (date[:7], region)
        groups.setdefault(key, []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': r, agg + '_revenue_cents': _aggregate(groups[(m,r)], agg)}
            for m,r in sorted(groups, key=lambda k: (str(k[0]), str(k[1])))]


def lookup(rows, lookup, request):
    targets = {r.get('region'): r.get('target') for r in lookup}
    out = _revenue(rows, request)
    for row in out:
        target = targets.get(row.get('region'))
        value = row['revenue_cents']
        row['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value / target
    return out


def window(rows, lookup, request):
    out = _revenue(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, row in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
