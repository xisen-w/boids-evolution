"""Native implementations of the tabular publication service families."""
from statistics import median


def _filled(rows, request):
    mode = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero' or not vals:
        value = 0
    elif mode == 'mean':
        value = sum(vals) / len(vals)
    elif mode == 'median':
        value = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out = []
    for row in rows:
        item = dict(row)
        if item.get('units') is None:
            item['units'] = value
        if item.get('region') is not None:
            item['region'] = item['region'].strip().lower()
        out.append(item)
    return out


def clean(rows, lookup, request):
    return _filled(rows, request)


def _revenue(rows, request, normalize=True):
    base = _filled(rows, request)
    for item in base:
        u, p = item.get('units'), item.get('price_cents')
        item['revenue_cents'] = None if u is None or p is None else u * p
    return base


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(vals) if vals else 0
    if agg == 'count':
        return len(vals)
    if agg == 'mean':
        return sum(vals) / len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    data = _revenue(rows, request)
    groups = {}
    for row in data:
        key = row.get('region')
        if key is not None:
            groups.setdefault(key, []).append(row.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    field = agg + '_revenue_cents'
    return [{'region': k, field: _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    data = _revenue(rows, request)
    groups = {}
    for row in data:
        region = row.get('region')
        date = row.get('date')
        month = date[:7] if date is not None else None
        if region is not None and month is not None:
            groups.setdefault((month, region), []).append(row.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    field = agg + '_revenue_cents'
    keys = sorted(groups, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': r, field: _aggregate(groups[(m, r)], agg)} for m, r in keys]


def lookup_service(rows, lookup, request):
    data = _revenue(rows, request)
    targets = {item.get('region'): item.get('target') for item in lookup}
    for row in data:
        region = row.get('region')
        target = targets.get(region)
        revenue_value = row.get('revenue_cents')
        row['revenue_cents_per_target'] = (None if target is None or target == 0 or revenue_value is None
                                             else revenue_value / target)
    return data


def window(rows, lookup, request):
    data = _revenue(rows, request)
    size = request.get('window', 2)
    if size not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    values = []
    for i, row in enumerate(data):
        values.append(row.get('revenue_cents'))
        trailing = values[max(0, i + 1 - size):i + 1]
        valid = [v for v in trailing if v is not None]
        row['roll_revenue_cents'] = sum(valid) / len(valid) if valid else None
    return data


__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup_service', 'window']
