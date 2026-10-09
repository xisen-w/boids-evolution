"""Pure-Python row-table services."""
from statistics import mean, median


def _fill(rows, request):
    mode = request.get('fill', 'zero')
    if mode not in ('zero', 'mean', 'median'):
        raise ValueError('fill must be zero, mean, or median')
    values = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = 0 if mode == 'zero' or not values else (mean(values) if mode == 'mean' else median(values))
    return [({**r, 'units': replacement if r.get('units') is None else r.get('units')}) for r in rows]


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _base_revenue(rows, request):
    result = []
    for row in _fill(rows, request):
        units, price = row.get('units'), row.get('price_cents')
        rev = None if units is None or price is None else units * price
        result.append({**row, 'revenue_cents': rev})
    return result


def clean(rows, lookup, request):
    return [{**r, 'region': _region(r.get('region'))} for r in _fill(rows, request)]


def revenue(rows, lookup, request):
    return _base_revenue(rows, request)


def _normalized_revenue(rows, request):
    return [{**r, 'region': _region(r.get('region'))} for r in _base_revenue(rows, request)]


def _aggregate(values, agg):
    values = [v for v in values if v is not None]
    if agg == 'sum': return sum(values)
    if agg == 'count': return len(values)
    if agg == 'mean': return sum(values) / len(values) if values else None
    raise ValueError('agg must be sum, mean, or count')


def group(rows, lookup, request):
    groups = {}
    for r in _normalized_revenue(rows, request):
        key = r.get('region')
        if key is not None: groups.setdefault(key, []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    groups = {}
    for r in _normalized_revenue(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None: groups.setdefault((month, region), []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(groups[(m, r)], agg)}
            for m, r in sorted(groups, key=lambda k: (str(k[0]), str(k[1])))]


def lookup(rows, lookup, request):
    targets = {_region(x.get('region')): x.get('target') for x in lookup if x.get('region') is not None}
    result = []
    for r in _normalized_revenue(rows, request):
        target, rev = targets.get(r.get('region')), r.get('revenue_cents')
        value = None if target is None or target == 0 or rev is None else rev / target
        result.append({**r, 'revenue_cents_per_target': value})
    return result


def window(rows, lookup, request):
    data = _base_revenue(rows, request)
    width = request.get('window', 2)
    if width not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    output = []
    for i, row in enumerate(data):
        vals = [x['revenue_cents'] for x in data[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        output.append({**row, 'roll_revenue_cents': sum(vals)/len(vals) if vals else None})
    return output
