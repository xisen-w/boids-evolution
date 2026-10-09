"""Native implementations of the tabular service families."""
from statistics import mean, median


def _filled(rows, fill):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero':
        replacement = 0
    elif fill == 'mean':
        replacement = sum(vals) / len(vals) if vals else 0
    elif fill == 'median':
        replacement = median(vals) if vals else 0
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out = []
    for row in rows:
        d = dict(row)
        if d.get('units') is None:
            d['units'] = replacement
        out.append(d)
    return out


def _normalize(rows, request):
    out = _filled(rows, request['fill'])
    for row in out:
        if row.get('region') is not None:
            row['region'] = row['region'].strip().lower()
    return out


def _revenue_rows(rows, request):
    out = _normalize(rows, request)
    for row in out:
        u, p = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    return _normalize(rows, request)


def revenue(rows, lookup, request):
    return _revenue_rows(rows, request)


def _aggregate(values, agg):
    if agg == 'sum':
        return sum(values)
    if agg == 'count':
        return len(values)
    if agg == 'mean':
        return sum(values) / len(values) if values else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def _groups(rows, request, monthly=False):
    data = _revenue_rows(rows, request)
    buckets = {}
    for row in data:
        region = row.get('region')
        month = (row.get('date')[:7] if row.get('date') is not None else None) if monthly else None
        if region is None or (monthly and month is None):
            continue
        key = (month, region) if monthly else (region,)
        buckets.setdefault(key, []).append(row['revenue_cents'])
    agg = request['agg']
    name = f'{agg}_revenue_cents'
    result = []
    keys = sorted(buckets, key=lambda k: tuple(str(x) for x in k))
    for key in keys:
        vals = [v for v in buckets[key] if v is not None]
        item = ({'month': key[0], 'region': key[1]} if monthly else {'region': key[0]})
        item[name] = _aggregate(vals, agg)
        result.append(item)
    return result


def group(rows, lookup, request):
    return _groups(rows, request)


def monthly(rows, lookup, request):
    return _groups(rows, request, monthly=True)


def lookup_service(rows, lookup, request):
    out = _revenue_rows(rows, request)
    targets = {item.get('region'): item.get('target') for item in lookup}
    for row in out:
        region, rev = row.get('region'), row.get('revenue_cents')
        target = targets.get(region)
        row['revenue_cents_per_target'] = None if region not in targets or target is None or target == 0 or rev is None else rev / target
    return out


def window(rows, lookup, request):
    out = _revenue_rows(rows, request)
    n = request['window']
    if n not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    revenues = [r['revenue_cents'] for r in out]
    for i, row in enumerate(out):
        vals = [v for v in revenues[max(0, i - n + 1):i + 1] if v is not None]
        row['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out

# Explicit convenience alias matching the family name.
lookup = lookup_service
