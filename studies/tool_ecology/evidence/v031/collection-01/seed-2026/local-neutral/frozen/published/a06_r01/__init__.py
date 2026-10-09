"""Native implementations of the tabular service families."""
from statistics import mean, median


def _norm(value):
    return value.strip().lower() if isinstance(value, str) else value


def _filled(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    fill = (sum(vals) / len(vals) if mode == 'mean' and vals else
            median(vals) if mode == 'median' and vals else 0)
    return [dict(r, region=_norm(r.get('region')),
                 units=(fill if r.get('units') is None else r.get('units'))) for r in rows]


def _revenue_rows(rows, request):
    result = _filled(rows, request)
    for r, source in zip(result, rows):
        u = r.get('units')
        p = source.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return result


def clean(rows, lookup, request):
    return _filled(rows, request)


def revenue(rows, lookup, request):
    return _revenue_rows(rows, request)


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals) / len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    data = _revenue_rows(rows, request)
    groups = {}
    for r in data:
        key = r.get('region')
        if key is not None:
            groups.setdefault(key, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    field = agg + '_revenue_cents'
    return [{'region': k, field: _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    data = _revenue_rows(rows, request)
    groups = {}
    for r in data:
        region = r.get('region')
        date = r.get('date')
        month = date[:7] if date is not None else None
        if region is not None and month is not None:
            groups.setdefault((month, region), []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    field = agg + '_revenue_cents'
    return [{'month': m, 'region': r, field: _aggregate(groups[(m, r)], agg)}
            for m, r in sorted(groups, key=lambda x: (str(x[0]), str(x[1])))]


def lookup(rows, lookup, request):
    data = _revenue_rows(rows, request)
    targets = {_norm(item.get('region')): item.get('target') for item in lookup}
    for r in data:
        target = targets.get(r.get('region'))
        rev = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return data


def window(rows, lookup, request):
    data = _revenue_rows(rows, request)
    width = request.get('window', 2)
    for i, r in enumerate(data):
        vals = [x['revenue_cents'] for x in data[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return data

clean_service = clean
revenue_service = revenue
group_service = group
monthly_service = monthly
lookup_service = lookup
window_service = window
