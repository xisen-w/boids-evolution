"""Native implementations of the tabular publication service families."""
from statistics import mean, median


def _fill(rows, request):
    values = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    replacement = 0 if not values else (mean(values) if mode == 'mean' else median(values) if mode == 'median' else 0)
    result = []
    for row in rows:
        x = dict(row)
        if x.get('units') is None:
            x['units'] = replacement
        result.append(x)
    return result


def _region(region):
    return None if region is None else region.strip().lower()


def _revenue(rows, request):
    out = []
    for row in _fill(rows, request):
        x = dict(row)
        u, p = x.get('units'), x.get('price_cents')
        x['revenue_cents'] = None if u is None or p is None else u * p
        out.append(x)
    return out


def clean(rows, lookup, request):
    out = _fill(rows, request)
    for x in out:
        x['region'] = _region(x.get('region'))
    return out


def revenue(rows, lookup, request):
    out = _revenue(rows, request)
    for x in out:
        x['region'] = _region(x.get('region'))
    return out


def _aggregate(values, agg):
    if agg == 'count':
        return len(values)
    if agg == 'mean':
        return None if not values else sum(values) / len(values)
    return sum(values)


def _groups(items, keys, request):
    buckets = {}
    for item in items:
        key = tuple(item.get(k) for k in keys)
        if any(v is None for v in key):
            continue
        buckets.setdefault(key, []).append(item.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    name = agg + '_revenue_cents'
    result = []
    for key in sorted(buckets, key=lambda k: tuple(str(v) for v in k)):
        vals = [v for v in buckets[key] if v is not None]
        result.append(dict(zip(keys, key), **{name: _aggregate(vals, agg)}))
    return result


def group(rows, lookup, request):
    items = _revenue(rows, request)
    for x in items:
        x['region'] = _region(x.get('region'))
    return _groups(items, ['region'], request)


def monthly(rows, lookup, request):
    items = _revenue(rows, request)
    for x in items:
        x['region'] = _region(x.get('region'))
        d = x.get('date')
        x['month'] = None if d is None else d[:7]
    return _groups(items, ['month', 'region'], request)


def lookup(rows, lookup, request):
    items = revenue(rows, lookup, request)
    targets = {}
    for rec in lookup:
        key = _region(rec.get('region'))
        if key is not None:
            targets[key] = rec.get('target')
    for x in items:
        target = targets.get(x.get('region'))
        value = x.get('revenue_cents')
        x['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value / target
    return items


def window(rows, lookup, request):
    items = _revenue(rows, request)
    n = request.get('window', 2)
    for i, x in enumerate(items):
        vals = [item['revenue_cents'] for item in items[max(0, i-n+1):i+1] if item['revenue_cents'] is not None]
        x['roll_revenue_cents'] = None if not vals else sum(vals) / len(vals)
    return items
