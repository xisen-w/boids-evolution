"""Native implementations of the recurring tabular service families."""
from statistics import mean, median


def _base(rows, request, normalize=True):
    """Copy rows and normalize/fill/derive fields without mutating inputs."""
    fill = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = {'zero': 0, 'mean': (mean(vals) if vals else 0), 'median': (median(vals) if vals else 0)}.get(fill)
    if fill not in ('zero', 'mean', 'median'):
        raise ValueError("fill must be zero, mean, or median")
    out = []
    for source in rows:
        r = dict(source)
        if normalize and r.get('region') is not None:
            r['region'] = r['region'].strip().lower()
        if r.get('units') is None:
            r['units'] = replacement
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
        out.append(r)
    return out


def clean(rows, lookup, request):
    # Clean does not derive revenue.
    out = []
    fill = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero': replacement = 0
    elif fill == 'mean': replacement = mean(vals) if vals else 0
    elif fill == 'median': replacement = median(vals) if vals else 0
    else: raise ValueError('fill must be zero, mean, or median')
    for src in rows:
        r = dict(src)
        if r.get('region') is not None: r['region'] = r['region'].strip().lower()
        if r.get('units') is None: r['units'] = replacement
        out.append(r)
    return out


def revenue(rows, lookup, request):
    return _base(rows, request, normalize=False)


def _aggregate(vals, agg):
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return mean(vals) if vals else None
    raise ValueError('agg must be sum, mean, or count')


def group(rows, lookup, request):
    data = _base(rows, request)
    agg = request.get('agg', 'sum')
    groups = {}
    for r in data:
        key = r.get('region')
        if key is None: continue
        groups.setdefault(key, []).append(r['revenue_cents'])
    return [{'region': key, f'{agg}_revenue_cents': _aggregate([v for v in vals if v is not None], agg)}
            for key, vals in sorted(groups.items(), key=lambda item: str(item[0]))]


def monthly(rows, lookup, request):
    data = _base(rows, request)
    agg = request.get('agg', 'sum')
    groups = {}
    for r in data:
        region = r.get('region')
        date = r.get('date')
        month = date[:7] if date is not None else None
        if region is None or month is None: continue
        groups.setdefault((month, region), []).append(r['revenue_cents'])
    keys = sorted(groups, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': reg, f'{agg}_revenue_cents': _aggregate([v for v in groups[(m, reg)] if v is not None], agg)} for m, reg in keys]


def lookup(rows, lookup, request):
    data = _base(rows, request)
    targets = {}
    for item in lookup:
        key = item.get('region')
        if key is not None: targets[key.strip().lower()] = item.get('target')
    for r in data:
        target = targets.get(r.get('region'))
        revenue_value = r['revenue_cents']
        r['revenue_cents_per_target'] = None if target is None or target == 0 or revenue_value is None else revenue_value / target
    return data


def window(rows, lookup, request):
    data = _base(rows, request, normalize=False)
    n = request.get('window', 2)
    if n not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(data):
        values = [x['revenue_cents'] for x in data[max(0, i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = mean(values) if values else None
    return data
