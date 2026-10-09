"""Reusable row-oriented table transformations for the six publication service families."""
from statistics import mean, median


def _fill(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    method = request.get('fill', 'zero')
    if not vals:
        replacement = 0
    elif method == 'mean':
        replacement = mean(vals)
    elif method == 'median':
        replacement = median(vals)
    else:
        replacement = 0
    return [dict(r, **({'units': replacement} if r.get('units') is None else {})) for r in rows]


def clean(rows, lookup, request):
    out = _fill(rows, request)
    for row in out:
        if row.get('region') is not None:
            row['region'] = row['region'].strip().lower()
    return out


def revenue(rows, lookup, request):
    out = clean(rows, lookup, request)
    for row in out:
        u, p = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if u is None or p is None else u * p
    return out


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'count':
        return len(vals)
    if agg == 'mean':
        return sum(vals) / len(vals) if vals else None
    return sum(vals) if vals else 0


def _groups(entries, agg, keys):
    grouped = {}
    for key, value in entries:
        grouped.setdefault(key, []).append(value)
    result = []
    for key, vals in grouped.items():
        key = key if isinstance(key, tuple) else (key,)
        row = {k: v for k, v in zip(keys, key)}
        row[agg + '_revenue_cents'] = _aggregate(vals, agg)
        result.append(row)
    result.sort(key=lambda r: tuple(str(r[k]) for k in keys))
    return result


def group(rows, lookup, request):
    agg = request.get('agg', 'sum')
    data = revenue(rows, lookup, request)
    entries = []
    for r in data:
        region = r.get('region')
        if region is not None:
            entries.append((region, r['revenue_cents']))
    return _groups(entries, agg, ['region'])


def monthly(rows, lookup, request):
    agg = request.get('agg', 'sum')
    data = revenue(rows, lookup, request)
    entries = []
    for r in data:
        region, date = r.get('region'), r.get('date')
        if region is not None and date is not None:
            entries.append(((date[:7], region), r['revenue_cents']))
    return _groups(entries, agg, ['month', 'region'])


def lookup_rate(rows, lookup, request):
    data = revenue(rows, lookup, request)
    targets = {}
    for item in lookup:
        region = item.get('region')
        if region is not None:
            targets[region.strip().lower()] = item.get('target')
    for row in data:
        target = targets.get(row.get('region'))
        rev = row.get('revenue_cents')
        row['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return data


def window(rows, lookup, request):
    data = revenue(rows, lookup, request)
    size = request.get('window', 2)
    for i, row in enumerate(data):
        vals = [r['revenue_cents'] for r in data[max(0, i-size+1):i+1] if r['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return data


clean_service = clean
revenue_service = revenue
group_service = group
monthly_service = monthly
lookup_service = lookup_rate
window_service = window
