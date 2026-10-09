"""Native implementations of six tabular service families."""
from statistics import mean, median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _prepare(rows, request):
    """Copy rows, normalize region, impute units, append revenue."""
    out = [dict(row) for row in rows]
    for row in out:
        row['region'] = _region(row.get('region'))
    missing = [r for r in out if r.get('units') is None]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    fill = request.get('fill', 'zero')
    if fill == 'zero' or not vals:
        replacement = 0
    elif fill == 'mean':
        replacement = mean(vals)
    elif fill == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be zero, mean, or median")
    for row in missing:
        row['units'] = replacement
    for row in out:
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return out


def clean(rows, lookup, request):
    out = [dict(row) for row in rows]
    for row in out:
        row['region'] = _region(row.get('region'))
    vals = [r.get('units') for r in out if r.get('units') is not None]
    fill = request.get('fill', 'zero')
    if fill == 'zero' or not vals:
        replacement = 0
    elif fill == 'mean':
        replacement = mean(vals)
    elif fill == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be zero, mean, or median")
    for row in out:
        if row.get('units') is None:
            row['units'] = replacement
    return out


def revenue(rows, lookup, request):
    return _prepare(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(present)
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return mean(present) if present else None
    raise ValueError("agg must be sum, mean, or count")


def group(rows, lookup, request):
    data = _prepare(rows, request)
    groups = {}
    for r in data:
        key = r.get('region')
        if key is not None:
            groups.setdefault(key, []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(v, agg)}
            for k, v in sorted(groups.items(), key=lambda item: str(item[0]))]


def monthly(rows, lookup, request):
    data = _prepare(rows, request)
    groups = {}
    for r in data:
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    keys = sorted(groups, key=lambda pair: (str(pair[0]), str(pair[1])))
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(groups[(m, r)], agg)} for m, r in keys]


def lookup(rows, lookup, request):
    data = _prepare(rows, request)
    targets = {}
    for item in lookup:
        targets[_region(item.get('region'))] = item.get('target')
    for row in data:
        target = targets.get(row.get('region'))
        rev = row.get('revenue_cents')
        row['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return data


def window(rows, lookup, request):
    data = _prepare(rows, request)
    size = request.get('window', 2)
    if size not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    vals = []
    for i, row in enumerate(data):
        vals.append(row.get('revenue_cents'))
        trailing = [x for x in vals[max(0, i-size+1):i+1] if x is not None]
        row['roll_revenue_cents'] = mean(trailing) if trailing else None
    return data
