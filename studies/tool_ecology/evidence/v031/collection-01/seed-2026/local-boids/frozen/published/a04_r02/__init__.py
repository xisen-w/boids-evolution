"""Pure-Python adapters for recurring tabular transforms."""
from statistics import median


def _fill(rows, request):
    mode = request.get('fill', 'zero')
    values = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero': value = 0
    elif mode == 'mean': value = sum(values) / len(values) if values else 0
    elif mode == 'median': value = median(values) if values else 0
    else: raise ValueError('fill must be zero, mean, or median')
    result = []
    for row in rows:
        r = dict(row)
        if r.get('units') is None: r['units'] = value
        result.append(r)
    return result


def _normalize(rows):
    for r in rows:
        if isinstance(r.get('region'), str): r['region'] = r['region'].strip().lower()
    return rows


def _derive(rows, request, normalize=False):
    out = _fill(rows, request)
    if normalize: _normalize(out)
    for r in out:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    return _normalize(_fill(rows, request))


def revenue(rows, lookup, request):
    return _derive(rows, request)


def _agg(values, agg):
    if agg not in ('sum', 'mean', 'count'): raise ValueError('agg must be sum, mean, or count')
    values = [v for v in values if v is not None]
    if agg == 'sum': return sum(values)
    if agg == 'count': return len(values)
    return sum(values) / len(values) if values else None


def group(rows, lookup, request):
    agg = request.get('agg', 'sum'); groups = {}
    for r in _derive(rows, request, True):
        key = r.get('region')
        if key is not None: groups.setdefault(key, []).append(r['revenue_cents'])
    return [{'region': k, f'{agg}_revenue_cents': _agg(v, agg)} for k, v in sorted(groups.items(), key=lambda x: str(x[0]))]


def monthly(rows, lookup, request):
    agg = request.get('agg', 'sum'); groups = {}
    for r in _derive(rows, request, True):
        month = r.get('date')
        month = month[:7] if month is not None else None
        region = r.get('region')
        if month is not None and region is not None: groups.setdefault((month, region), []).append(r['revenue_cents'])
    return [{'month': m, 'region': reg, f'{agg}_revenue_cents': _agg(v, agg)} for (m, reg), v in sorted(groups.items(), key=lambda x: (str(x[0][0]), str(x[0][1])))]


def lookup(rows, lookup, request):
    out = _derive(rows, request, True)
    targets = {}
    for item in lookup:
        key = item.get('region')
        if isinstance(key, str): targets[key.strip().lower()] = item.get('target')
    for r in out:
        target, rev = targets.get(r.get('region')), r['revenue_cents']
        r['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return out


def window(rows, lookup, request):
    out = _derive(rows, request)
    width = request.get('window', 2)
    if width not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
