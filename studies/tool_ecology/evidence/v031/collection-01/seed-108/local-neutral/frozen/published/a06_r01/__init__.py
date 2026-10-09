"""Reusable table transformations for the six publication service families."""
from statistics import mean, median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _filled(rows, request):
    mode = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'mean':
        replacement = mean(vals) if vals else 0
    elif mode == 'median':
        replacement = median(vals) if vals else 0
    else:
        replacement = 0
    result = []
    for row in rows:
        out = dict(row)
        out['region'] = _region(out.get('region'))
        if out.get('units') is None:
            out['units'] = replacement
        result.append(out)
    return result


def clean(rows, lookup, request):
    """Normalize region and fill units; preserve all fields and row order."""
    return _filled(rows, request)


def revenue(rows, lookup, request):
    """Clean rows and append revenue_cents (None if an operand is missing)."""
    result = _filled(rows, request)
    for row in result:
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return result


def _aggregate(values, agg):
    values = [v for v in values if v is not None]
    if agg == 'count':
        return len(values)
    if agg == 'mean':
        return mean(values) if values else None
    return sum(values)


def group(rows, lookup, request):
    """Return sorted normalized-region revenue aggregates."""
    groups = {}
    for row in revenue(rows, lookup, request):
        key = row.get('region')
        if key is not None:
            groups.setdefault(key, []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    col = agg + '_revenue_cents'
    return [{'region': key, col: _aggregate(groups[key], agg)}
            for key in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    """Return sorted month/region revenue aggregates."""
    groups = {}
    for row in revenue(rows, lookup, request):
        region, date = row.get('region'), row.get('date')
        month = date[:7] if date is not None else None
        if region is not None and month is not None:
            groups.setdefault((month, region), []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    col = agg + '_revenue_cents'
    return [{'month': m, 'region': r, col: _aggregate(groups[(m, r)], agg)}
            for m, r in sorted(groups, key=lambda k: (str(k[0]), str(k[1])))]


def lookup_revenue(rows, lookup, request):
    """Append revenue and exact normalized-region revenue-per-target values."""
    targets = {_region(item.get('region')): item.get('target') for item in lookup}
    result = revenue(rows, lookup, request)
    for row in result:
        target = targets.get(row.get('region'))
        value = row['revenue_cents']
        row['revenue_cents_per_target'] = (None if target is None or target == 0 or value is None
                                           else value / target)
    return result


def window(rows, lookup, request):
    """Append trailing ROWS mean of nonmissing revenue."""
    result = revenue(rows, lookup, request)
    size = request.get('window', 2)
    for i, row in enumerate(result):
        vals = [x['revenue_cents'] for x in result[max(0, i-size+1):i+1]
                if x['revenue_cents'] is not None]
        row['roll_revenue_cents'] = mean(vals) if vals else None
    return result
