"""Native row-oriented implementations of the six table service families."""
from statistics import median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _fill_rows(rows, request):
    """Copy rows and fill missing units according to request.fill."""
    copied = [dict(row) for row in rows]
    values = [r.get('units') for r in copied if r.get('units') is not None]
    method = request.get('fill')
    if method == 'zero' or not values:
        replacement = 0
    elif method == 'mean':
        replacement = sum(values) / len(values)
    elif method == 'median':
        replacement = median(values)
    else:
        raise ValueError("request.fill must be 'zero', 'mean', or 'median'")
    for row in copied:
        if row.get('units') is None:
            row['units'] = replacement
    return copied


def clean(rows, lookup, request):
    out = _fill_rows(rows, request)
    for row in out:
        row['region'] = _region(row.get('region'))
    return out


def _revenue(rows, request):
    out = _fill_rows(rows, request)
    for row in out:
        row['region'] = _region(row.get('region'))
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return out


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(present)
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return sum(present) / len(present) if present else None
    raise ValueError("request.agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    grouped = {}
    for row in _revenue(rows, request):
        key = row.get('region')
        if key is not None:
            grouped.setdefault(key, []).append(row.get('revenue_cents'))
    agg = request.get('agg')
    return [{'region': key, f'{agg}_revenue_cents': _aggregate(vals, agg)}
            for key, vals in sorted(grouped.items(), key=lambda item: str(item[0]))]


def monthly(rows, lookup, request):
    grouped = {}
    for row in _revenue(rows, request):
        date, region = row.get('date'), row.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            grouped.setdefault((month, region), []).append(row.get('revenue_cents'))
    agg = request.get('agg')
    return [{'month': month, 'region': region,
             f'{agg}_revenue_cents': _aggregate(vals, agg)}
            for (month, region), vals in sorted(grouped.items(), key=lambda item: (str(item[0][0]), str(item[0][1])))]


def lookup(rows, lookup, request):
    out = _revenue(rows, request)
    targets = {_region(item.get('region')): item.get('target') for item in lookup}
    for row in out:
        target, amount = targets.get(row.get('region')), row.get('revenue_cents')
        row['revenue_cents_per_target'] = (None if target in (None, 0) or amount is None
                                           else amount / target)
    return out


def window(rows, lookup, request):
    out = _revenue(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4):
        raise ValueError('request.window must be 2, 3, or 4')
    for i, row in enumerate(out):
        values = [r['revenue_cents'] for r in out[max(0, i-width+1):i+1]
                  if r['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(values) / len(values) if values else None
    return out
