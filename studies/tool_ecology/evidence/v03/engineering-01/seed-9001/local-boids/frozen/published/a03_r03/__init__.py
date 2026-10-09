"""Reusable, non-mutating table transformations."""
from statistics import median


def _fill(rows, request):
    mode = (request or {}).get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode not in ('zero', 'mean', 'median'):
        raise ValueError('fill must be zero, mean, or median')
    if mode == 'zero' or not vals:
        return 0
    return sum(vals) / len(vals) if mode == 'mean' else median(vals)


def _normalized(row):
    result = dict(row)
    if result.get('region') is not None:
        result['region'] = result['region'].strip().lower()
    return result


def _filled(rows, request):
    fill = _fill(rows, request)
    out = []
    for row in rows:
        r = dict(row)
        if r.get('units') is None:
            r['units'] = fill
        out.append(r)
    return out


def _derive(rows):
    for r in rows:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return rows


def clean(rows, lookup, request):
    return [_normalized(r) for r in _filled(rows, request)]


def revenue(rows, lookup, request):
    return _derive(_filled(rows, request))


def _agg(values, mode):
    values = [v for v in values if v is not None]
    if mode == 'sum': return sum(values)
    if mode == 'count': return len(values)
    if mode == 'mean': return sum(values) / len(values) if values else None
    raise ValueError('agg must be sum, mean, or count')


def group(rows, lookup, request):
    mode = (request or {}).get('agg', 'sum')
    groups = {}
    for row in revenue(rows, lookup, request):
        key = row.get('region')
        key = key.strip().lower() if key is not None else None
        if key is not None:
            groups.setdefault(key, []).append(row['revenue_cents'])
    return [{'region': k, mode + '_revenue_cents': _agg(groups[k], mode)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    mode = (request or {}).get('agg', 'sum')
    groups = {}
    for row in revenue(rows, lookup, request):
        region, date = row.get('region'), row.get('date')
        month = date[:7] if date is not None else None
        region = region.strip().lower() if region is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(row['revenue_cents'])
    keys = sorted(groups, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': r, mode + '_revenue_cents': _agg(groups[(m, r)], mode)} for m, r in keys]


def lookup(rows, lookup, request):
    out = [_normalized(r) for r in revenue(rows, lookup, request)]
    targets = {}
    for item in lookup:
        key = item.get('region')
        if key is not None:
            targets[key.strip().lower()] = item.get('target')
    for row in out:
        target = targets.get(row.get('region'))
        value = row['revenue_cents']
        row['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value / target
    return out


def window(rows, lookup, request):
    width = (request or {}).get('window', 2)
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    out = _derive(_filled(rows, request))
    for i, row in enumerate(out):
        values = [r['revenue_cents'] for r in out[max(0, i-width+1):i+1] if r['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(values) / len(values) if values else None
    return out
