"""Reusable table transforms for the publication service families."""
from statistics import median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _filled(rows, request):
    fill = request.get('fill', 'zero')
    values = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero' or not values:
        replacement = 0
    elif fill == 'mean':
        replacement = sum(values) / len(values)
    elif fill == 'median':
        replacement = median(values)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out = []
    for row in rows:
        r = dict(row)
        r['region'] = _region(r.get('region'))
        if r.get('units') is None:
            r['units'] = replacement
        out.append(r)
    return out


def _revenue(rows, request):
    out = _filled(rows, request)
    for r in out:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    return _filled(rows, request)


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _aggregate(vals, agg):
    if agg == 'sum':
        return sum(vals)
    if agg == 'count':
        return len(vals)
    if agg == 'mean':
        return sum(vals) / len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    agg = request.get('agg', 'sum')
    groups = {}
    for r in _revenue(rows, request):
        key = r.get('region')
        if key is not None:
            groups.setdefault(key, []).append(r['revenue_cents'])
    return [{'region': k, f'{agg}_revenue_cents': _aggregate([v for v in vs if v is not None], agg)}
            for k, vs in sorted(groups.items(), key=lambda item: str(item[0]))]


def monthly(rows, lookup, request):
    agg = request.get('agg', 'sum')
    groups = {}
    for r in _revenue(rows, request):
        date = r.get('date')
        month = date[:7] if date is not None else None
        region = r.get('region')
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r['revenue_cents'])
    return [{'month': m, 'region': reg, f'{agg}_revenue_cents': _aggregate([v for v in vs if v is not None], agg)}
            for (m, reg), vs in sorted(groups.items(), key=lambda item: (str(item[0][0]), str(item[0][1])))]


def lookup(rows, lookup, request):
    out = _revenue(rows, request)
    targets = {_region(x.get('region')): x.get('target') for x in lookup if x.get('region') is not None}
    for r in out:
        region, rev = r.get('region'), r.get('revenue_cents')
        target = targets.get(region)
        r['revenue_cents_per_target'] = None if rev is None or target is None or target == 0 else rev / target
    return out


def window(rows, lookup, request):
    out = _revenue(rows, request)
    width = request.get('window', 2)
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
