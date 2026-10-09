"""Native implementations of the tabular service families."""
from statistics import median

_MISSING = object()

def _normalized(value):
    return value.strip().lower() if isinstance(value, str) else value

def _fill_value(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if method == 'zero' or not vals:
        return 0
    if method == 'mean':
        return sum(vals) / len(vals)
    if method == 'median':
        return median(vals)
    raise ValueError("request.fill must be zero, mean, or median")

def _base(rows, request):
    rows = list(rows)
    fill = _fill_value(rows, request.get('fill', 'zero'))
    out = []
    for row in rows:
        item = dict(row)
        item['region'] = _normalized(item.get('region'))
        if item.get('units') is None:
            item['units'] = fill
        out.append(item)
    return out

def clean(rows, lookup, request):
    return _base(rows, request)

def _revenue_rows(rows, request):
    # Revenue and window preserve region exactly; only clean/group/monthly/lookup normalize it.
    original = [dict(r) for r in rows]
    fill = _fill_value(original, request.get('fill', 'zero'))
    out = original
    for row in out:
        if row.get('units') is None:
            row['units'] = fill
    for row in out:
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return out

def revenue(rows, lookup, request):
    return _revenue_rows(rows, request)

def _aggregate(values, agg):
    valid = [v for v in values if v is not None]
    if agg == 'sum': return sum(valid)
    if agg == 'count': return len(valid)
    if agg == 'mean': return sum(valid) / len(valid) if valid else None
    raise ValueError("request.agg must be sum, mean, or count")

def _groups(rows, request, monthly=False):
    data = _revenue_rows(rows, request)
    grouped = {}
    for row in data:
        region = _normalized(row.get('region'))
        month = row.get('date')[:7] if row.get('date') is not None else None
        if region is None or (monthly and month is None):
            continue
        key = (month, region) if monthly else (region,)
        grouped.setdefault(key, []).append(row.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    result = []
    for key in sorted(grouped, key=lambda k: tuple(str(x) for x in k)):
        value = _aggregate(grouped[key], agg)
        if monthly:
            result.append({'month': key[0], 'region': key[1], agg + '_revenue_cents': value})
        else:
            result.append({'region': key[0], agg + '_revenue_cents': value})
    return result

def group(rows, lookup, request):
    return _groups(rows, request)

def monthly(rows, lookup, request):
    return _groups(rows, request, monthly=True)

def lookup(rows, lookup, request):
    out = _revenue_rows(rows, request)
    targets = {_normalized(item.get('region')): item.get('target') for item in lookup}
    for row in out:
        row['region'] = _normalized(row.get('region'))
        region, rev = row.get('region'), row.get('revenue_cents')
        target = targets.get(region)
        row['revenue_cents_per_target'] = None if rev is None or target is None or target == 0 else rev / target
    return out

def window(rows, lookup, request):
    out = _revenue_rows(rows, request)
    size = request.get('window')
    if size not in (2, 3, 4):
        raise ValueError('request.window must be 2, 3, or 4')
    for i, row in enumerate(out):
        values = [x['revenue_cents'] for x in out[max(0, i-size+1):i+1] if x['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(values) / len(values) if values else None
    return out
