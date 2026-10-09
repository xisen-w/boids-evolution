"""Small, non-mutating implementations of the recurring table services."""
from statistics import median


def _filled(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill')
    if mode == 'zero' or not vals:
        fill = 0
    elif mode == 'mean':
        fill = sum(vals) / len(vals)
    elif mode == 'median':
        fill = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    result = []
    for row in rows:
        item = dict(row)
        if item.get('units') is None:
            item['units'] = fill
        result.append(item)
    return result


def _base(rows, request):
    result = _filled(rows, request)
    for row in result:
        region = row.get('region')
        row['region'] = region.strip().lower() if isinstance(region, str) else region
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return result


def clean(rows, lookup, request):
    result = _filled(rows, request)
    for row in result:
        region = row.get('region')
        row['region'] = region.strip().lower() if isinstance(region, str) else region
    return result


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(values, agg):
    values = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(values)
    if agg == 'count':
        return len(values)
    if agg == 'mean':
        return sum(values) / len(values) if values else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    buckets = {}
    for row in _base(rows, request):
        key = row.get('region')
        if key is not None:
            buckets.setdefault(key, []).append(row.get('revenue_cents'))
    agg = request.get('agg')
    return [{'region': key, agg + '_revenue_cents': _aggregate(buckets[key], agg)}
            for key in sorted(buckets, key=str)]


def monthly(rows, lookup, request):
    buckets = {}
    for row in _base(rows, request):
        region = row.get('region')
        date = row.get('date')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            buckets.setdefault((month, region), []).append(row.get('revenue_cents'))
    agg = request.get('agg')
    return [{'month': month, 'region': region,
             agg + '_revenue_cents': _aggregate(buckets[(month, region)], agg)}
            for month, region in sorted(buckets, key=lambda k: (str(k[0]), str(k[1])))]


def lookup(rows, lookup, request):
    targets = {r.get('region'): r.get('target') for r in lookup}
    result = _base(rows, request)
    for row in result:
        target = targets.get(row.get('region'))
        revenue_value = row.get('revenue_cents')
        row['revenue_cents_per_target'] = (None if target is None or target == 0 or revenue_value is None
                                           else revenue_value / target)
    return result


def window(rows, lookup, request):
    result = _base(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for i, row in enumerate(result):
        vals = [r['revenue_cents'] for r in result[max(0, i-width+1):i+1]
                if r['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return result
