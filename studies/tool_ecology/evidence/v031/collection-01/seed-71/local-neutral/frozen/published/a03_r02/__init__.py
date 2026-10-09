"""Reusable table transformations for the six publication service families."""
from statistics import median


def _fill_units(rows, method):
    values = [r.get('units') for r in rows if r.get('units') is not None]
    if not values:
        replacement = 0
    elif method == 'zero':
        replacement = 0
    elif method == 'mean':
        replacement = sum(values) / len(values)
    elif method == 'median':
        replacement = median(values)
    else:
        raise ValueError("fill must be zero, mean, or median")
    return [replacement if r.get('units') is None else r.get('units') for r in rows]


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _base(rows, request):
    units = _fill_units(rows, request.get('fill'))
    result = []
    for row, unit in zip(rows, units):
        out = dict(row)
        out['units'] = unit
        price = row.get('price_cents')
        out['revenue_cents'] = None if unit is None or price is None else unit * price
        result.append(out)
    return result


def clean(rows, lookup, request):
    units = _fill_units(rows, request.get('fill'))
    out = []
    for row, unit in zip(rows, units):
        item = dict(row)
        item['region'] = _region(row.get('region'))
        item['units'] = unit
        out.append(item)
    return out


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(groups, agg):
    if agg not in ('sum', 'mean', 'count'):
        raise ValueError("agg must be sum, mean, or count")
    def calc(vals):
        vals = [v for v in vals if v is not None]
        if agg == 'count': return len(vals)
        if agg == 'sum': return sum(vals)
        return sum(vals) / len(vals) if vals else None
    return calc


def group(rows, lookup, request):
    data = _base(rows, request)
    for row in data: row['region'] = _region(row.get('region'))
    agg = request.get('agg')
    calc = _aggregate({}, agg)
    groups = {}
    for row in data:
        key = row.get('region')
        if key is not None: groups.setdefault(key, []).append(row['revenue_cents'])
    name = agg + '_revenue_cents'
    return [{'region': key, name: calc(vals)} for key, vals in sorted(groups.items(), key=lambda kv: str(kv[0]))]


def monthly(rows, lookup, request):
    data = _base(rows, request)
    for row in data: row['region'] = _region(row.get('region'))
    agg = request.get('agg')
    calc = _aggregate({}, agg)
    groups = {}
    for row in data:
        date, region = row.get('date'), row.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(row['revenue_cents'])
    name = agg + '_revenue_cents'
    keys = sorted(groups, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': r, name: calc(groups[(m, r)])} for m, r in keys]


def lookup_service(rows, lookup, request):
    data = _base(rows, request)
    for row in data:
        row['region'] = _region(row.get('region'))
    targets = {item.get('region'): item.get('target') for item in lookup}
    for row in data:
        target = targets.get(row.get('region'))
        rev = row['revenue_cents']
        row['revenue_cents_per_target'] = None if target in (None, 0) or rev is None else rev / target
    return data


def window(rows, lookup, request):
    data = _base(rows, request)
    size = request.get('window')
    if size not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, row in enumerate(data):
        vals = [x['revenue_cents'] for x in data[max(0, i-size+1):i+1] if x['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return data

# Root adapters have the same signature required by publication checks.
lookup = lookup_service

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
