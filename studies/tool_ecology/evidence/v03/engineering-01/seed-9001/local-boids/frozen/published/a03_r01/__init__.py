"""Native implementations of the recurring table service families."""
from statistics import median


def _fill(rows, request):
    mode = request.get('fill', 'zero') if request else 'zero'
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero' or not vals:
        return 0
    if mode == 'mean':
        return sum(vals) / len(vals)
    if mode == 'median':
        return median(vals)
    raise ValueError("fill must be zero, mean, or median")


def _base(rows, request):
    fill = _fill(rows, request)
    result = []
    for row in rows:
        r = dict(row)
        if r.get('region') is not None:
            r['region'] = r['region'].strip().lower()
        if r.get('units') is None:
            r['units'] = fill
        result.append(r)
    return result


def clean(rows, lookup, request):
    return _base(rows, request)


def revenue(rows, lookup, request):
    out = _base(rows, request)
    for r in out:
        r['revenue_cents'] = None if r.get('units') is None or r.get('price_cents') is None else r['units'] * r['price_cents']
    return out


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals) / len(vals) if vals else None
    raise ValueError("agg must be sum, mean, or count")


def group(rows, lookup, request):
    agg = request.get('agg', 'sum')
    groups = {}
    for r in revenue(rows, lookup, request):
        key = r.get('region')
        if key is not None:
            groups.setdefault(key, []).append(r['revenue_cents'])
    return [{'region': k, agg + '_revenue_cents': _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    agg = request.get('agg', 'sum')
    groups = {}
    for r in revenue(rows, lookup, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r['revenue_cents'])
    keys = sorted(groups, key=lambda x: (str(x[0]), str(x[1])))
    return [{'month': m, 'region': reg, agg + '_revenue_cents': _aggregate(groups[(m, reg)], agg)} for m, reg in keys]


def lookup(rows, lookup, request):
    out = revenue(rows, lookup, request)
    targets = {r.get('region'): r.get('target') for r in lookup}
    for r in out:
        target = targets.get(r.get('region'))
        value = r['revenue_cents']
        r['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value / target
    return out


def window(rows, lookup, request):
    out = revenue(rows, lookup, request)
    width = request.get('window', 2)
    if width not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
