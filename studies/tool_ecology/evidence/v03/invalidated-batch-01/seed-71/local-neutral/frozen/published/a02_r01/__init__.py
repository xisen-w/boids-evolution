"""Native implementations of the tabular service families."""
from statistics import mean, median


def _filled(rows, request):
    values = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero' or not values:
        replacement = 0
    elif mode == 'mean':
        replacement = mean(values)
    elif mode == 'median':
        replacement = median(values)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [dict(r, units=(r.get('units') if r.get('units') is not None else replacement)) for r in rows]


def _region(r):
    value = r.get('region')
    return value.strip().lower() if isinstance(value, str) else value


def _normalized(rows, request):
    out = _filled(rows, request)
    for r in out:
        r['region'] = _region(r)
    return out


def _revenue_rows(rows, request):
    out = _normalized(rows, request)
    for r in out:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    return _normalized(rows, request)


def revenue(rows, lookup, request):
    return _revenue_rows(rows, request)


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return mean(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    data = _revenue_rows(rows, request)
    buckets = {}
    for r in data:
        key = r.get('region')
        if key is not None: buckets.setdefault(key, []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'region': k, agg + '_revenue_cents': _aggregate(v, agg)}
            for k, v in sorted(buckets.items(), key=lambda kv: str(kv[0]))]


def monthly(rows, lookup, request):
    data = _revenue_rows(rows, request)
    buckets = {}
    for r in data:
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            buckets.setdefault((month, region), []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': r, agg + '_revenue_cents': _aggregate(v, agg)}
            for (m, r), v in sorted(buckets.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1])))]


def lookup_family(rows, lookup, request):
    data = _revenue_rows(rows, request)
    targets = {item.get('region'): item.get('target') for item in lookup}
    for r in data:
        target = targets.get(r.get('region'))
        value = r.get('revenue_cents')
        r['revenue_cents_per_target'] = (None if target is None or target == 0 or value is None else value / target)
    return data


def window(rows, lookup, request):
    data = _revenue_rows(rows, request)
    n = request.get('window', 2)
    if n not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(data):
        vals = [x['revenue_cents'] for x in data[max(0, i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = mean(vals) if vals else None
    return data

# Published adapter names follow the six service family names.
lookup_service = lookup_family
