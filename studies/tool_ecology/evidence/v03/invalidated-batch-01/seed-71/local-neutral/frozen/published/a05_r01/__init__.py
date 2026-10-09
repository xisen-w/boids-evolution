"""Native row-oriented implementations of the publication service families."""
from statistics import mean, median

_MISSING = object()

def _filled_units(rows, mode):
    values = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero' or not values:
        fill = 0
    elif mode == 'mean':
        fill = mean(values)
    elif mode == 'median':
        fill = median(values)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [fill if r.get('units') is None else r.get('units') for r in rows]

def _base(rows, request):
    units = _filled_units(rows, request.get('fill'))
    out = []
    for row, unit in zip(rows, units):
        item = dict(row)
        item['region'] = row.get('region').strip().lower() if row.get('region') is not None else None
        item['units'] = unit
        price = row.get('price_cents')
        item['revenue_cents'] = None if unit is None or price is None else unit * price
        out.append(item)
    return out

def clean(rows, lookup, request):
    """Normalize region and fill units, preserving all row fields and order."""
    units = _filled_units(rows, request.get('fill'))
    result = []
    for row, unit in zip(rows, units):
        item = dict(row)
        item['region'] = row.get('region').strip().lower() if row.get('region') is not None else None
        item['units'] = unit
        result.append(item)
    return result

def revenue(rows, lookup, request):
    """Fill units and derive revenue_cents for each row."""
    return _base(rows, request)

def _aggregate(items, agg):
    if agg not in ('sum', 'mean', 'count'):
        raise ValueError("agg must be 'sum', 'mean', or 'count'")
    vals = [x for x in items if x is not None]
    if agg == 'count': return len(vals)
    if agg == 'sum': return sum(vals)
    return mean(vals) if vals else None

def group(rows, lookup, request):
    """Aggregate nonmissing revenue by normalized, nonmissing region."""
    buckets = {}
    for row in _base(rows, request):
        key = row['region']
        if key is not None: buckets.setdefault(key, []).append(row['revenue_cents'])
    agg = request.get('agg')
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(v, agg)}
            for k, v in sorted(buckets.items(), key=lambda kv: str(kv[0]))]

def monthly(rows, lookup, request):
    """Aggregate nonmissing revenue by month and normalized region."""
    buckets = {}
    for row in _base(rows, request):
        month = row.get('date')[:7] if row.get('date') is not None else None
        region = row['region']
        if month is not None and region is not None:
            buckets.setdefault((month, region), []).append(row['revenue_cents'])
    agg = request.get('agg')
    keys = sorted(buckets, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(buckets[(m,r)], agg)} for m,r in keys]

def lookup(rows, lookup, request):
    """Add revenue per target using exact keys from lookup rows."""
    result = _base(rows, request)
    targets = {item.get('region'): item.get('target') for item in lookup}
    for item in result:
        target = targets.get(item['region'], _MISSING)
        revenue_value = item['revenue_cents']
        item['revenue_cents_per_target'] = (None if target is _MISSING or target is None or target == 0 or revenue_value is None else revenue_value / target)
    return result

def window(rows, lookup, request):
    """Add trailing ROWS-window mean of available revenue."""
    result = _base(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, item in enumerate(result):
        vals = [r['revenue_cents'] for r in result[max(0, i-width+1):i+1] if r['revenue_cents'] is not None]
        item['roll_revenue_cents'] = mean(vals) if vals else None
    return result
