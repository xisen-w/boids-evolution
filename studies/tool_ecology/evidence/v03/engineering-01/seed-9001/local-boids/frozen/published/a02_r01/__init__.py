"""Native implementations of the recurring table services."""
from statistics import median


def _normalized(value):
    return value.strip().lower() if isinstance(value, str) else value


def _prepare(rows, request):
    """Copy rows, normalize regions, fill missing units, and derive revenue."""
    result = [dict(row) for row in rows]
    for row in result:
        row['region'] = _normalized(row.get('region'))
    missing_values = [r.get('units') for r in result if r.get('units') is not None]
    fill = request.get('fill', 'zero')
    if fill == 'zero' or not missing_values:
        replacement = 0
    elif fill == 'mean':
        replacement = sum(missing_values) / len(missing_values)
    elif fill == 'median':
        replacement = median(missing_values)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    for row in result:
        if row.get('units') is None:
            row['units'] = replacement
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return result


def clean(rows, lookup, request):
    result = [dict(row) for row in rows]
    for row in result:
        row['region'] = _normalized(row.get('region'))
    values = [r.get('units') for r in result if r.get('units') is not None]
    fill = request.get('fill', 'zero')
    if fill == 'zero' or not values:
        replacement = 0
    elif fill == 'mean':
        replacement = sum(values) / len(values)
    elif fill == 'median':
        replacement = median(values)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    for row in result:
        if row.get('units') is None:
            row['units'] = replacement
    return result


def revenue(rows, lookup, request):
    return _prepare(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(present)
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return sum(present) / len(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def _group(rows, request, monthly=False):
    prepared = _prepare(rows, request)
    agg = request.get('agg', 'sum')
    groups = {}
    for row in prepared:
        region = row.get('region')
        month = row.get('date')[:7] if isinstance(row.get('date'), str) else None
        if region is None or (monthly and month is None):
            continue
        key = (month, region) if monthly else region
        groups.setdefault(key, []).append(row.get('revenue_cents'))
    output = []
    for key in sorted(groups, key=lambda k: tuple(str(x) for x in k) if isinstance(k, tuple) else str(k)):
        amount = _aggregate(groups[key], agg)
        if monthly:
            output.append({'month': key[0], 'region': key[1], f'{agg}_revenue_cents': amount})
        else:
            output.append({'region': key, f'{agg}_revenue_cents': amount})
    return output


def group(rows, lookup, request):
    return _group(rows, request)


def monthly(rows, lookup, request):
    return _group(rows, request, monthly=True)


def lookup(rows, lookup, request):
    result = _prepare(rows, request)
    targets = {}
    for item in lookup:
        key = _normalized(item.get('region'))
        targets[key] = item.get('target')
    for row in result:
        target = targets.get(row.get('region'))
        rev = row.get('revenue_cents')
        row['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return result


def window(rows, lookup, request):
    result = _prepare(rows, request)
    size = request.get('window', 2)
    if size not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    revenues = []
    for i, row in enumerate(result):
        revenues.append(row.get('revenue_cents'))
        values = [v for v in revenues[max(0, i-size+1):i+1] if v is not None]
        row['roll_revenue_cents'] = sum(values) / len(values) if values else None
    return result
