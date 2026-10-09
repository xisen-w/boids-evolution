"""Reusable transformations for sales-row service requests."""
from statistics import median


def _is_missing(value):
    return value is None


def _fill_values(rows, mode):
    values = [row.get('units') for row in rows if not _is_missing(row.get('units'))]
    if mode == 'zero':
        replacement = 0
    elif not values:
        replacement = 0
    elif mode == 'mean':
        replacement = sum(values) / len(values)
    elif mode == 'median':
        replacement = median(values)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [replacement if _is_missing(row.get('units')) else row.get('units') for row in rows]


def _prepare(rows, request, normalize=False, derive=True):
    filled = _fill_values(rows, request.get('fill', 'zero'))
    output = []
    for original, units in zip(rows, filled):
        row = dict(original)
        if normalize and row.get('region') is not None:
            row['region'] = row['region'].strip().lower()
        if 'units' in row or any(_is_missing(r.get('units')) for r in rows):
            row['units'] = units
        if derive:
            p = row.get('price_cents')
            row['revenue_cents'] = None if units is None or p is None else units * p
        output.append(row)
    return output


def clean(rows, lookup, request):
    return _prepare(rows, request, normalize=True, derive=False)


def revenue(rows, lookup, request):
    return _prepare(rows, request)


def _aggregate(items, agg):
    vals = [v for v in items if v is not None]
    if agg == 'sum':
        return sum(vals) if vals else 0
    if agg == 'count':
        return len(vals)
    if agg == 'mean':
        return sum(vals) / len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def _groups(rows, request, monthly=False):
    prepared = _prepare(rows, request, normalize=True)
    groups = {}
    for row in prepared:
        region = row.get('region')
        month = row.get('date')
        month = month[:7] if month is not None else None
        if region is None or (monthly and month is None):
            continue
        key = (month, region) if monthly else (region,)
        groups.setdefault(key, []).append(row.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    result = []
    for key in sorted(groups, key=lambda k: tuple(str(x) for x in k)):
        val = _aggregate(groups[key], agg)
        if monthly:
            result.append({'month': key[0], 'region': key[1], agg + '_revenue_cents': val})
        else:
            result.append({'region': key[0], agg + '_revenue_cents': val})
    return result


def group(rows, lookup, request):
    return _groups(rows, request)


def monthly(rows, lookup, request):
    return _groups(rows, request, monthly=True)


def lookup(rows, lookup, request):
    prepared = _prepare(rows, request, normalize=True)
    targets = {}
    for entry in lookup:
        region = entry.get('region')
        if region is not None:
            targets[region.strip().lower()] = entry.get('target')
    for row in prepared:
        target = targets.get(row.get('region'))
        revenue_value = row.get('revenue_cents')
        row['revenue_cents_per_target'] = (revenue_value / target
            if target is not None and target != 0 and revenue_value is not None else None)
    return prepared


def window(rows, lookup, request):
    prepared = _prepare(rows, request)
    width = request.get('window', 2)
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    revenues = []
    for i, row in enumerate(prepared):
        revenues.append(row.get('revenue_cents'))
        values = [v for v in revenues[max(0, i-width+1):i+1] if v is not None]
        row['roll_revenue_cents'] = sum(values) / len(values) if values else None
    return prepared
