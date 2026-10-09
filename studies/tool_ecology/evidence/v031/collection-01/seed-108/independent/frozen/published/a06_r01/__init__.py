"""Small pure-Python table transforms for the publication service families."""
from statistics import mean, median


def _prepare(rows, request):
    """Copy rows, normalize region, fill units, and append revenue."""
    out = [dict(row) for row in rows]
    units = [r.get('units') for r in out if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'mean':
        replacement = mean(units) if units else 0
    elif mode == 'median':
        replacement = median(units) if units else 0
    else:
        replacement = 0
    for r in out:
        region = r.get('region')
        if region is not None:
            r['region'] = region.strip().lower()
        if r.get('units') is None:
            r['units'] = replacement
        units, price = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if units is None or price is None else units * price
    return out


def clean(rows, lookup, request):
    out = [dict(r) for r in rows]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    fill = request.get('fill', 'zero')
    value = mean(vals) if fill == 'mean' and vals else median(vals) if fill == 'median' and vals else 0
    for r in out:
        if r.get('region') is not None:
            r['region'] = r['region'].strip().lower()
        if r.get('units') is None:
            r['units'] = value
    return out


def revenue(rows, lookup, request):
    return _prepare(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return mean(present) if present else None
    return sum(present)


def group(rows, lookup, request):
    data = _prepare(rows, request)
    groups = {}
    for r in data:
        key = r.get('region')
        if key is not None:
            groups.setdefault(key, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    name = agg + '_revenue_cents'
    return [{'region': k, name: _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    data = _prepare(rows, request)
    groups = {}
    for r in data:
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    name = agg + '_revenue_cents'
    keys = sorted(groups, key=lambda pair: (str(pair[0]), str(pair[1])))
    return [{'month': m, 'region': r, name: _aggregate(groups[(m, r)], agg)} for m, r in keys]


def lookup(rows, lookup, request):
    data = _prepare(rows, request)
    targets = {}
    for entry in lookup:
        region = entry.get('region')
        if region is not None:
            targets[region.strip().lower()] = entry.get('target')
    for r in data:
        target = targets.get(r.get('region'))
        revenue_value = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target is None or target == 0 or revenue_value is None else revenue_value / target
    return data


def window(rows, lookup, request):
    data = _prepare(rows, request)
    width = request.get('window', 2)
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(data):
        vals = [x['revenue_cents'] for x in data[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = mean(vals) if vals else None
    return data
