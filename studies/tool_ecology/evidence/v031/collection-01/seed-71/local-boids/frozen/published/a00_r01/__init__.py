"""Native adapters for the recurring table service families."""
from statistics import mean, median


def _fill_units(rows, request):
    values = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if not values:
        replacement = 0
    elif mode == 'zero':
        replacement = 0
    elif mode == 'mean':
        replacement = mean(values)
    elif mode == 'median':
        replacement = median(values)
    else:
        raise ValueError("fill must be zero, mean, or median")
    return [replacement if r.get('units') is None else r.get('units') for r in rows]


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def clean(rows, lookup, request):
    units = _fill_units(rows, request)
    out = []
    for row, unit in zip(rows, units):
        item = dict(row)
        item['region'] = _region(row.get('region'))
        item['units'] = unit
        out.append(item)
    return out


def _revenue_rows(rows, request):
    units = _fill_units(rows, request)
    out = []
    for row, unit in zip(rows, units):
        item = dict(row)
        item['region'] = _region(row.get('region'))
        item['units'] = unit
        price = row.get('price_cents')
        item['revenue_cents'] = None if unit is None or price is None else unit * price
        out.append(item)
    return out


def revenue(rows, lookup, request):
    return _revenue_rows(rows, request)


def _aggregate(vals, agg):
    good = [x for x in vals if x is not None]
    if agg == 'sum':
        return sum(good)
    if agg == 'count':
        return len(good)
    if agg == 'mean':
        return sum(good) / len(good) if good else None
    raise ValueError("agg must be sum, mean, or count")


def group(rows, lookup, request):
    records = _revenue_rows(rows, request)
    groups = {}
    for r in records:
        key = r.get('region')
        if key is not None:
            groups.setdefault(key, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': k, agg + '_revenue_cents': _aggregate(groups[k], agg)}
            for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    records = _revenue_rows(rows, request)
    groups = {}
    for r in records:
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': r, agg + '_revenue_cents': _aggregate(groups[(m, r)], agg)}
            for m, r in sorted(groups, key=lambda x: (str(x[0]), str(x[1])))]


def lookup(rows, lookup, request):
    records = _revenue_rows(rows, request)
    targets = {r.get('region'): r.get('target') for r in lookup if r.get('region') is not None}
    for item in records:
        target = targets.get(item.get('region'))
        rev = item['revenue_cents']
        item['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return records


def window(rows, lookup, request):
    records = _revenue_rows(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for i, item in enumerate(records):
        vals = [r['revenue_cents'] for r in records[max(0, i-width+1):i+1] if r['revenue_cents'] is not None]
        item['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return records
