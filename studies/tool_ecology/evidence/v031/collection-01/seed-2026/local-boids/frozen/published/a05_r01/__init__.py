"""Reusable table transformations for the publication service families."""
from statistics import median


def _norm(value):
    return value.strip().lower() if isinstance(value, str) else value


def _filled(rows, request):
    """Copy rows and normalize region; fill units according to request."""
    result = [dict(row) for row in rows]
    values = [r.get('units') for r in result if r.get('units') is not None]
    mode = request['fill']
    if mode == 'zero':
        replacement = 0
    elif mode == 'mean':
        replacement = sum(values) / len(values) if values else 0
    elif mode == 'median':
        replacement = median(values) if values else 0
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    for r in result:
        r['region'] = _norm(r.get('region'))
        if r.get('units') is None:
            r['units'] = replacement
    return result


def clean(rows, lookup, request):
    """Normalize regions and fill units; preserve all fields and row order."""
    return _filled(rows, request)


def _revenue(rows, request):
    result = _filled(rows, request)
    for r in result:
        units, price = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if units is None or price is None else units * price
    return result


def revenue(rows, lookup, request):
    """Fill units, then append revenue_cents (None if an operand is missing)."""
    return _revenue(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(present)
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return sum(present) / len(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def _keysort(value):
    return str(value)


def group(rows, lookup, request):
    """Aggregate revenue by normalized region, omitting missing regions."""
    data = _revenue(rows, request)
    buckets = {}
    for r in data:
        key = r.get('region')
        if key is not None:
            buckets.setdefault(key, []).append(r['revenue_cents'])
    agg = request['agg']
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(buckets[k], agg)}
            for k in sorted(buckets, key=_keysort)]


def monthly(rows, lookup, request):
    """Aggregate revenue by (date month, normalized region), omitting null keys."""
    buckets = {}
    for r in _revenue(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            buckets.setdefault((month, region), []).append(r['revenue_cents'])
    agg = request['agg']
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(buckets[(m, r)], agg)}
            for m, r in sorted(buckets, key=lambda pair: (_keysort(pair[0]), _keysort(pair[1])))]


def lookup(rows, lookup, request):
    """Add exact normalized-region revenue/target; never append lookup metadata."""
    targets = {_norm(entry.get('region')): entry.get('target') for entry in lookup}
    result = _revenue(rows, request)
    for r in result:
        target = targets.get(r.get('region'))
        revenue_value = r['revenue_cents']
        r['revenue_cents_per_target'] = (None if target is None or target == 0 or revenue_value is None
                                         else revenue_value / target)
    return result


def window(rows, lookup, request):
    """Append trailing ROWS mean of nonmissing revenue, including current row."""
    data = _revenue(rows, request)
    width = request['window']
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    vals = []
    for i, r in enumerate(data):
        vals.append(r['revenue_cents'])
        recent = [v for v in vals[max(0, i + 1 - width):i + 1] if v is not None]
        r['roll_revenue_cents'] = sum(recent) / len(recent) if recent else None
    return data
