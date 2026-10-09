"""Native adapters for tabular service families."""
from statistics import mean, median


def _norm(value):
    return value.strip().lower() if isinstance(value, str) else value


def _filled(rows, request, normalize=True):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero' or not vals:
        replacement = 0
    elif mode == 'mean':
        replacement = sum(vals) / len(vals)
    elif mode == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out = []
    for row in rows:
        item = dict(row)
        if normalize:
            item['region'] = _norm(item.get('region'))
        if item.get('units') is None:
            item['units'] = replacement
        out.append(item)
    return out


def _revenue(rows, request, normalize=False):
    out = _filled(rows, request, normalize=normalize)
    for row, source in zip(out, rows):
        units = row.get('units')
        price = source.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return out


def clean(rows, lookup, request):
    return _filled(rows, request)


def revenue(rows, lookup, request):
    return _revenue(rows, request, normalize=False)


def _aggregate(values, agg):
    values = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(values)
    if agg == 'count':
        return len(values)
    if agg == 'mean':
        return sum(values) / len(values) if values else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def _group(rows, request, monthly=False):
    data = _revenue(rows, request, normalize=True)
    agg = request.get('agg', 'sum')
    buckets = {}
    for row in data:
        region = row.get('region')
        month = row.get('date')[:7] if row.get('date') is not None else None
        if region is None or (monthly and month is None):
            continue
        key = (month, region) if monthly else (region,)
        buckets.setdefault(key, []).append(row.get('revenue_cents'))
    result = []
    for key, vals in buckets.items():
        record = {}
        if monthly:
            record.update(month=key[0], region=key[1])
        else:
            record['region'] = key[0]
        record[agg + '_revenue_cents'] = _aggregate(vals, agg)
        result.append(record)
    result.sort(key=lambda x: tuple(str(x[k]) for k in (('month', 'region') if monthly else ('region',))))
    return result


def group(rows, lookup, request):
    return _group(rows, request)


def monthly(rows, lookup, request):
    return _group(rows, request, True)


def lookup(rows, lookup, request):
    data = _revenue(rows, request, normalize=True)
    targets = {_norm(entry.get('region')): entry.get('target') for entry in lookup}
    for row in data:
        target = targets.get(row.get('region'))
        rev = row.get('revenue_cents')
        row['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return data


def window(rows, lookup, request):
    data = _revenue(rows, request)
    width = request.get('window', 2)
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for i, row in enumerate(data):
        vals = [x['revenue_cents'] for x in data[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return data

# Explicit root adapters used by package consumers.
clean_check = clean
revenue_check = revenue
group_check = group
monthly_check = monthly
lookup_check = lookup
window_check = window
