"""Native adapters for the recurring tabular data services."""
from statistics import mean, median


def _filled(rows, fill):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = 0 if not vals else (mean(vals) if fill == 'mean' else median(vals) if fill == 'median' else 0)
    out = []
    for row in rows:
        item = dict(row)
        if item.get('units') is None:
            item['units'] = replacement
        out.append(item)
    return out


def _base(rows, request):
    out = _filled(rows, request.get('fill', 'zero'))
    for r in out:
        r['region'] = r.get('region').strip().lower() if isinstance(r.get('region'), str) else r.get('region')
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    out = _filled(rows, request.get('fill', 'zero'))
    for r in out:
        r['region'] = r.get('region').strip().lower() if isinstance(r.get('region'), str) else r.get('region')
    return out


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(vals, agg):
    good = [v for v in vals if v is not None]
    if agg == 'count': return len(good)
    if agg == 'mean': return sum(good) / len(good) if good else None
    return sum(good)


def group(rows, lookup, request):
    buckets = {}
    for r in _base(rows, request):
        key = r.get('region')
        if key is not None: buckets.setdefault(key, []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'region': k, agg + '_revenue_cents': _aggregate(buckets[k], agg)} for k in sorted(buckets, key=str)]


def monthly(rows, lookup, request):
    buckets = {}
    for r in _base(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            buckets.setdefault((month, region), []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'month': k[0], 'region': k[1], agg + '_revenue_cents': _aggregate(buckets[k], agg)}
            for k in sorted(buckets, key=lambda x: (str(x[0]), str(x[1])))]


def lookup(rows, lookup, request):
    out = _base(rows, request)
    targets = {x.get('region'): x.get('target') for x in lookup}
    for r in out:
        target, value = targets.get(r.get('region')), r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target in (None, 0) or value is None else value / target
    return out


def window(rows, lookup, request):
    out = _base(rows, request)
    width = request.get('window', 2)
    revenues = []
    for i, r in enumerate(out):
        revenues.append(r.get('revenue_cents'))
        vals = [v for v in revenues[max(0, i-width+1):i+1] if v is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
