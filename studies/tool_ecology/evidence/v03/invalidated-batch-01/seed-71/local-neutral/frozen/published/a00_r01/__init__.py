"""Native implementations of the tabular service families."""
from statistics import mean, median


def _fill_units(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if method == 'zero':
        replacement = 0
    elif method == 'mean':
        replacement = mean(vals) if vals else 0
    elif method == 'median':
        replacement = median(vals) if vals else 0
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [dict(r, units=(replacement if r.get('units') is None else r.get('units'))) for r in rows]


def _base(rows, request):
    result = _fill_units(rows, request.get('fill'))
    for row in result:
        region = row.get('region')
        row['region'] = region.strip().lower() if isinstance(region, str) else region
        u, p = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = u * p if u is not None and p is not None else None
    return result


def clean(rows, lookup, request):
    out = _fill_units(rows, request.get('fill'))
    for r in out:
        x = r.get('region')
        r['region'] = x.strip().lower() if isinstance(x, str) else x
    return out


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(values, agg):
    valid = [v for v in values if v is not None]
    if agg == 'sum': return sum(valid)
    if agg == 'count': return len(valid)
    if agg == 'mean': return sum(valid) / len(valid) if valid else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def _group(rows, request, monthly=False):
    data = _base(rows, request)
    buckets = {}
    for r in data:
        region = r.get('region')
        month = r.get('date')[:7] if isinstance(r.get('date'), str) else None
        key = (month, region) if monthly else region
        if any(x is None for x in key) if monthly else region is None:
            continue
        buckets.setdefault(key, []).append(r.get('revenue_cents'))
    agg = request.get('agg')
    keys = sorted(buckets, key=lambda k: tuple(str(x) for x in k) if isinstance(k, tuple) else str(k))
    output = []
    for key in keys:
        value = _aggregate(buckets[key], agg)
        # Empty valid-key groups do not arise from row input; sum/count identities are maintained by aggregate.
        if monthly:
            output.append({'month': key[0], 'region': key[1], f'{agg}_revenue_cents': value})
        else:
            output.append({'region': key, f'{agg}_revenue_cents': value})
    return output


def group(rows, lookup, request):
    return _group(rows, request)


def monthly(rows, lookup, request):
    return _group(rows, request, True)


def lookup(rows, lookup, request):
    data = _base(rows, request)
    targets = {}
    for item in lookup:
        key = item.get('region')
        if isinstance(key, str): key = key.strip().lower()
        targets[key] = item.get('target')
    for r in data:
        target = targets.get(r.get('region'))
        rev = r.get('revenue_cents')
        r['revenue_cents_per_target'] = rev / target if rev is not None and target not in (None, 0) else None
    return data


def window(rows, lookup, request):
    data = _base(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    revenues = []
    for i, r in enumerate(data):
        revenues.append(r.get('revenue_cents'))
        vals = [v for v in revenues[max(0, i-width+1):i+1] if v is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return data
