"""Native implementations of the tabular service families."""
from statistics import mean, median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _fill_units(rows, fill):
    values = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = {'zero': 0, 'mean': (mean(values) if values else 0),
                   'median': (median(values) if values else 0)}[fill]
    return [dict(r, region=_region(r.get('region')),
                 units=(replacement if r.get('units') is None else r.get('units'))) for r in rows]


def _revenue(rows, request):
    out = _fill_units(rows, request['fill'])
    for row in out:
        u, p = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    return _fill_units(rows, request['fill'])


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _aggregate(vals, agg):
    if agg == 'count': return len(vals)
    if agg == 'sum': return sum(vals)
    return mean(vals) if vals else None


def _group(rows, request, monthly=False):
    data = _revenue(rows, request)
    groups = {}
    for r in data:
        region = r.get('region')
        month = (r.get('date')[:7] if r.get('date') is not None else None) if monthly else None
        if region is None or (monthly and month is None): continue
        key = (month, region) if monthly else (region,)
        groups.setdefault(key, []).append(r['revenue_cents'])
    agg = request['agg']
    result = []
    for key, vals in groups.items():
        nonmissing = [v for v in vals if v is not None]
        result.append((key, _aggregate(nonmissing, agg)))
    result.sort(key=lambda item: tuple(str(x) for x in item[0]))
    if monthly:
        return [{'month': k[0], 'region': k[1], agg + '_revenue_cents': v} for k, v in result]
    return [{'region': k[0], agg + '_revenue_cents': v} for k, v in result]


def group(rows, lookup, request):
    return _group(rows, request)


def monthly(rows, lookup, request):
    return _group(rows, request, True)


def lookup(rows, lookup, request):
    data = _revenue(rows, request)
    targets = {_region(item.get('region')): item.get('target') for item in lookup}
    for r in data:
        target = targets.get(r.get('region'))
        value = r['revenue_cents']
        r['revenue_cents_per_target'] = None if target in (None, 0) or value is None else value / target
    return data


def window(rows, lookup, request):
    data = _revenue(rows, request)
    width = request['window']
    revenues = []
    for i, row in enumerate(data):
        revenues.append(row['revenue_cents'])
        vals = [v for v in revenues[max(0, i-width+1):i+1] if v is not None]
        row['roll_revenue_cents'] = mean(vals) if vals else None
    return data
