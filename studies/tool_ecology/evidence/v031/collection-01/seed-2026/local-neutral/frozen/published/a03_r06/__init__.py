"""Native implementations of the tabular service families."""
from statistics import mean, median


def _norm(x):
    return x.strip().lower() if isinstance(x, str) else x


def _filled(rows, request, normalize=True):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    method = request.get('fill', 'zero')
    if not vals:
        replacement = 0
    elif method == 'mean':
        replacement = mean(vals)
    elif method == 'median':
        replacement = median(vals)
    else:
        replacement = 0
    result = []
    for row in rows:
        x = dict(row)
        if normalize:
            x['region'] = _norm(x.get('region'))
        if x.get('units') is None:
            x['units'] = replacement
        result.append(x)
    return result


def _revenue(rows, request, normalize=True):
    data = _filled(rows, request, normalize=normalize)
    for r in data:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return data


def clean(rows, lookup, request):
    return _filled(rows, request)


def revenue(rows, lookup, request):
    return _revenue(rows, request, normalize=False)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return sum(present) / len(present) if present else None
    return sum(present) if present else 0


def group(rows, lookup, request):
    data = _revenue(rows, request)
    buckets = {}
    for r in data:
        key = r.get('region')
        if key is not None:
            buckets.setdefault(key, []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'region': k, agg + '_revenue_cents': _aggregate(v, agg)}
            for k, v in sorted(buckets.items(), key=lambda item: str(item[0]))]


def monthly(rows, lookup, request):
    data = _revenue(rows, request)
    buckets = {}
    for r in data:
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            buckets.setdefault((month, region), []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': r, agg + '_revenue_cents': _aggregate(v, agg)}
            for (m, r), v in sorted(buckets.items(), key=lambda item: (str(item[0][0]), str(item[0][1])))]


def lookup(rows, lookup, request):
    data = _revenue(rows, request)
    targets = {_norm(x.get('region')): x.get('target') for x in lookup}
    for r in data:
        region = r.get('region')
        target = targets.get(region) if region is not None else None
        val = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target is None or target == 0 or val is None else val / target
    return data


def window(rows, lookup, request):
    data = _revenue(rows, request, normalize=False)
    width = request.get('window', 2)
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(data):
        vals = [x['revenue_cents'] for x in data[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return data
