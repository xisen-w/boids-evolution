"""Native implementations of the recurring tabular service families."""
from statistics import median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _fill_value(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero' or not vals:
        return 0
    if mode == 'mean':
        return sum(vals) / len(vals)
    if mode == 'median':
        return median(vals)
    raise ValueError("fill must be 'zero', 'mean', or 'median'")


def _prepared(rows, request, normalize_region=False):
    fill = _fill_value(rows, request.get('fill', 'zero'))
    result = []
    for source in rows:
        row = dict(source)
        if normalize_region:
            row['region'] = _region(row.get('region'))
        if row.get('units') is None:
            row['units'] = fill
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
        result.append(row)
    return result


def clean(rows, lookup, request):
    del lookup
    fill = _fill_value(rows, request.get('fill', 'zero'))
    out = []
    for source in rows:
        row = dict(source)
        row['region'] = _region(row.get('region'))
        if row.get('units') is None:
            row['units'] = fill
        out.append(row)
    return out


def revenue(rows, lookup, request):
    del lookup
    return _prepared(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(present) if present else 0
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return sum(present) / len(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    del lookup
    agg = request.get('agg', 'sum')
    groups = {}
    for row in _prepared(rows, request, normalize_region=True):
        key = row.get('region')
        if key is not None:
            groups.setdefault(key, []).append(row['revenue_cents'])
    return [{'region': key, f'{agg}_revenue_cents': _aggregate(groups[key], agg)}
            for key in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    del lookup
    agg = request.get('agg', 'sum')
    groups = {}
    for row in _prepared(rows, request, normalize_region=True):
        date, region = row.get('date'), row.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(row['revenue_cents'])
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(groups[(m, r)], agg)}
            for m, r in sorted(groups, key=lambda k: (str(k[0]), str(k[1])))]


def lookup(rows, lookup, request):
    out = _prepared(rows, request, normalize_region=True)
    targets = {}
    for entry in lookup:
        targets[_region(entry.get('region'))] = entry.get('target')
    for row in out:
        target = targets.get(row.get('region'))
        value = row['revenue_cents']
        row['revenue_cents_per_target'] = (value / target
            if value is not None and target is not None and target != 0 else None)
    return out


def window(rows, lookup, request):
    del lookup
    out = _prepared(rows, request)
    width = request.get('window', 2)
    if not isinstance(width, int) or width <= 0:
        raise ValueError('window must be a positive integer')
    for i, row in enumerate(out):
        values = [r['revenue_cents'] for r in out[max(0, i-width+1):i+1]
                  if r['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(values) / len(values) if values else None
    return out
