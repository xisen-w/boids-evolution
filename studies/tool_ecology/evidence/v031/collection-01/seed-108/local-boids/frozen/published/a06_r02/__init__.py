"""Native implementations of the recurring tabular service families."""
from statistics import mean, median

_MISSING = object()

def _clone(rows):
    return [dict(row) for row in rows]

def _fill(rows, mode):
    values = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = {'zero': 0, 'mean': (mean(values) if values else 0), 'median': (median(values) if values else 0)}[mode]
    return [replacement if r.get('units') is None else r.get('units') for r in rows]

def _region(value):
    return value.strip().lower() if isinstance(value, str) else value

def _revenue_rows(rows, request, normalize_region=True):
    out = _clone(rows)
    units = _fill(rows, request.get('fill', 'zero'))
    for row, unit in zip(out, units):
        if normalize_region:
            row['region'] = _region(row.get('region'))
        price = row.get('price_cents')
        row['units'] = unit
        row['revenue_cents'] = None if unit is None or price is None else unit * price
    return out

def clean(rows, lookup, request):
    out = _clone(rows)
    units = _fill(rows, request.get('fill', 'zero'))
    for row, unit in zip(out, units):
        row['region'] = _region(row.get('region'))
        row['units'] = unit
    return out

def revenue(rows, lookup, request):
    return _revenue_rows(rows, request, normalize_region=False)

def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    return mean(vals) if vals else None

def group(rows, lookup, request):
    data = _revenue_rows(rows, request)
    buckets = {}
    for r in data:
        key = r.get('region')
        if key is not None: buckets.setdefault(key, []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'region': key, agg+'_revenue_cents': _aggregate(vals, agg)} for key, vals in sorted(buckets.items(), key=lambda kv: str(kv[0]))]

def monthly(rows, lookup, request):
    data = _revenue_rows(rows, request)
    buckets = {}
    for r in data:
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            buckets.setdefault((month, region), []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    keys = sorted(buckets, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': reg, agg+'_revenue_cents': _aggregate(buckets[(m,reg)], agg)} for m,reg in keys]

def lookup(rows, lookup, request):
    data = _revenue_rows(rows, request)
    targets = {_region(x.get('region')): x.get('target') for x in lookup}
    for r in data:
        target = targets.get(r.get('region'))
        value = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if value is None or target is None or target == 0 else value / target
    return data

def window(rows, lookup, request):
    data = _revenue_rows(rows, request, normalize_region=False)
    width = request.get('window', 2)
    for i, row in enumerate(data):
        vals = [r['revenue_cents'] for r in data[max(0, i-width+1):i+1] if r['revenue_cents'] is not None]
        row['roll_revenue_cents'] = mean(vals) if vals else None
    return data
