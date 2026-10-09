"""Dependency-free row-oriented implementations of the six table services."""
from statistics import median


def _prepare(rows, request, normalize=True):
    values = [r.get('units') for r in rows if r.get('units') is not None]
    fill = request['fill']
    if fill == 'zero': replacement = 0
    elif fill == 'mean': replacement = sum(values) / len(values) if values else 0
    elif fill == 'median': replacement = median(values) if values else 0
    else: raise ValueError("fill must be zero, mean, or median")
    result = []
    for source in rows:
        row = dict(source)
        if row.get('units') is None: row['units'] = replacement
        if normalize and row.get('region') is not None:
            row['region'] = row['region'].strip().lower()
        result.append(row)
    return result


def _with_revenue(rows, request, normalize=True):
    result = _prepare(rows, request, normalize)
    for r in result:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return result


def clean(rows, lookup, request):
    return _prepare(rows, request)


def revenue(rows, lookup, request):
    return _with_revenue(rows, request)


def _aggregate(values, agg):
    if agg == 'sum': return sum(values)
    if agg == 'count': return len(values)
    if agg == 'mean': return sum(values) / len(values) if values else None
    raise ValueError("agg must be sum, mean, or count")


def _group(rows, request, by_month):
    buckets = {}
    for r in _with_revenue(rows, request):
        region = r.get('region')
        date = r.get('date')
        month = date[:7] if date is not None else None
        if region is None or (by_month and month is None): continue
        key = (month, region) if by_month else (region,)
        buckets.setdefault(key, []).append(r['revenue_cents'])
    agg = request['agg']
    output = []
    for key in sorted(buckets, key=lambda k: tuple(str(x) for x in k)):
        vals = [x for x in buckets[key] if x is not None]
        item = {'month': key[0], 'region': key[1]} if by_month else {'region': key[0]}
        item[agg + '_revenue_cents'] = _aggregate(vals, agg)
        output.append(item)
    return output


def group(rows, lookup, request):
    return _group(rows, request, False)


def monthly(rows, lookup, request):
    return _group(rows, request, True)


def lookup_service(rows, lookup, request):
    result = _with_revenue(rows, request)
    targets = {entry.get('region'): entry.get('target') for entry in lookup}
    for r in result:
        region, rev = r.get('region'), r['revenue_cents']
        target = targets.get(region)
        r['revenue_cents_per_target'] = None if region not in targets or target is None or target == 0 or rev is None else rev / target
    return result


def window(rows, lookup, request):
    n = request['window']
    if n not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    result = _with_revenue(rows, request)
    revenues = [r['revenue_cents'] for r in result]
    for i, r in enumerate(result):
        vals = [v for v in revenues[max(0, i-n+1):i+1] if v is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return result


lookup = lookup_service
