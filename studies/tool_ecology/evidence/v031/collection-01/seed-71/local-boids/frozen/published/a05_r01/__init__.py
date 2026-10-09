"""Pure-Python row-oriented table services."""
from statistics import mean, median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _filled(rows, request):
    fill = request.get('fill', 'zero')
    values = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero' or not values:
        replacement = 0
    elif fill == 'mean':
        replacement = mean(values)
    elif fill == 'median':
        replacement = median(values)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    result = []
    for row in rows:
        item = dict(row)
        if item.get('units') is None:
            item['units'] = replacement
        result.append(item)
    return result


def _normalized(rows):
    result = []
    for row in rows:
        item = dict(row)
        if 'region' in item:
            item['region'] = _region(item['region'])
        result.append(item)
    return result


def clean(rows, lookup, request):
    return _normalized(_filled(rows, request))


def _revenue_rows(rows, request):
    result = _normalized(_filled(rows, request))
    for item in result:
        units, price = item.get('units'), item.get('price_cents')
        item['revenue_cents'] = None if units is None or price is None else units * price
    return result


def revenue(rows, lookup, request):
    return _revenue_rows(rows, request)


def _group(rows, keys, agg):
    groups = {}
    for row in rows:
        key = tuple(row.get(k) for k in keys)
        if any(v is None for v in key):
            continue
        groups.setdefault(key, []).append(row.get('revenue_cents'))
    output = []
    if agg not in ('sum', 'mean', 'count'):
        raise ValueError("agg must be 'sum', 'mean', or 'count'")
    for key, values in groups.items():
        values = [v for v in values if v is not None]
        if agg == 'sum':
            value = sum(values)
        elif agg == 'count':
            value = len(values)
        else:
            value = mean(values) if values else None
        item = dict(zip(keys, key))
        item[agg + '_revenue_cents'] = value
        output.append(item)
    output.sort(key=lambda item: tuple(str(item[k]) for k in keys))
    return output


def group(rows, lookup, request):
    return _group(_revenue_rows(rows, request), ['region'], request.get('agg', 'sum'))


def monthly(rows, lookup, request):
    data = _revenue_rows(rows, request)
    for item in data:
        date = item.get('date')
        item['month'] = date[:7] if date is not None else None
    return _group(data, ['month', 'region'], request.get('agg', 'sum'))


def lookup(rows, lookup, request):
    data = _revenue_rows(rows, request)
    targets = {}
    for item in lookup:
        key = _region(item.get('region'))
        targets[key] = item.get('target')
    for item in data:
        target = targets.get(item.get('region'))
        value = item.get('revenue_cents')
        item['revenue_cents_per_target'] = (
            value / target if value is not None and target is not None and target != 0 else None
        )
    return data


def window(rows, lookup, request):
    data = _revenue_rows(rows, request)
    size = request.get('window', 2)
    if not isinstance(size, int) or size <= 0:
        raise ValueError('window must be a positive integer')
    revenues = []
    for i, item in enumerate(data):
        revenues.append(item.get('revenue_cents'))
        recent = [v for v in revenues[max(0, i-size+1):i+1] if v is not None]
        item['roll_revenue_cents'] = mean(recent) if recent else None
    return data


__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
