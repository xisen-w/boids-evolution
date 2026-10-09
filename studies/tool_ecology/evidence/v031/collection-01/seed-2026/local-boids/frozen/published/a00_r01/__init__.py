"""Native implementations of the tabular service families."""
from statistics import mean, median

_MISSING = object()

def _region(value):
    return value.strip().lower() if isinstance(value, str) else value

def _fill_units(rows, mode):
    present = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'mean':
        replacement = mean(present) if present else 0
    elif mode == 'median':
        replacement = median(present) if present else 0
    else:
        replacement = 0
    return [dict(r, units=(r.get('units') if r.get('units') is not None else replacement)) for r in rows]

def _revenue_rows(rows, request):
    data = _fill_units(rows, request.get('fill', 'zero'))
    for row in data:
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return data

def clean(rows, lookup, request):
    data = _fill_units(rows, request.get('fill', 'zero'))
    for r in data:
        r['region'] = _region(r.get('region'))
    return data

def revenue(rows, lookup, request):
    return _revenue_rows(rows, request)

def _aggregate(values, agg):
    vals = [x for x in values if x is not None]
    if agg == 'mean': return mean(vals) if vals else None
    if agg == 'count': return len(vals)
    return sum(vals) if vals else 0

def group(rows, lookup, request):
    buckets = {}
    for r in _revenue_rows(rows, request):
        key = _region(r.get('region'))
        if key is not None: buckets.setdefault(key, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': k, agg+'_revenue_cents': _aggregate(v, agg)} for k,v in sorted(buckets.items(), key=lambda x: str(x[0]))]

def monthly(rows, lookup, request):
    buckets = {}
    for r in _revenue_rows(rows, request):
        region = _region(r.get('region'))
        date = r.get('date')
        month = date[:7] if date is not None else None
        if region is not None and month is not None:
            buckets.setdefault((month, region), []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    keys = sorted(buckets, key=lambda x: (str(x[0]), str(x[1])))
    return [{'month': m, 'region': r, agg+'_revenue_cents': _aggregate(buckets[(m,r)], agg)} for m,r in keys]

def lookup(rows, lookup, request):
    data = _revenue_rows(rows, request)
    targets = {item.get('region'): item.get('target') for item in lookup}
    for r in data:
        target = targets.get(_region(r.get('region')))
        value = r['revenue_cents']
        r['revenue_cents_per_target'] = None if target in (None, 0) or value is None else value / target
    return data

def window(rows, lookup, request):
    data = _revenue_rows(rows, request)
    size = request.get('window', 2)
    revenues = []
    for i, r in enumerate(data):
        revenues.append(r['revenue_cents'])
        values = [v for v in revenues[max(0, i-size+1):i+1] if v is not None]
        r['roll_revenue_cents'] = mean(values) if values else None
    return data
