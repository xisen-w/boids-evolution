"""Native implementations of recurring tabular service families."""
from statistics import mean, median


def _prepare(rows, request):
    """Copy rows and fill units; return copied rows with revenue appended."""
    out = [dict(row) for row in rows]
    missing = [r.get('units') is None for r in out]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero' or not vals:
        fill = 0
    elif mode == 'mean':
        fill = mean(vals)
    elif mode == 'median':
        fill = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    for r, absent in zip(out, missing):
        if absent:
            r['units'] = fill
        units, price = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if units is None or price is None else units * price
    return out


def clean(rows, lookup, request):
    out = [dict(r) for r in rows]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero' or not vals: fill = 0
    elif mode == 'mean': fill = mean(vals)
    elif mode == 'median': fill = median(vals)
    else: raise ValueError("fill must be 'zero', 'mean', or 'median'")
    for r in out:
        r['region'] = r.get('region').strip().lower() if r.get('region') is not None else None
        if r.get('units') is None: r['units'] = fill
    return out


def revenue(rows, lookup, request):
    out = _prepare(rows, request)
    for r in out:
        if r.get('region') is not None: r['region'] = r['region'].strip().lower()
    return out


def _aggregate(values, agg):
    present = [x for x in values if x is not None]
    if agg == 'sum': return sum(present)
    if agg == 'count': return len(present)
    if agg == 'mean': return mean(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    prepared = revenue(rows, lookup, request)
    buckets = {}
    for r in prepared:
        key = r.get('region')
        if key is not None: buckets.setdefault(key, []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'region': k, agg + '_revenue_cents': _aggregate(v, agg)} for k, v in sorted(buckets.items(), key=lambda p: str(p[0]))]


def monthly(rows, lookup, request):
    prepared = revenue(rows, lookup, request)
    buckets = {}
    for r in prepared:
        region = r.get('region')
        date = r.get('date')
        month = date[:7] if date is not None else None
        if region is not None and month is not None:
            buckets.setdefault((month, region), []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    keys = sorted(buckets, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': reg, agg + '_revenue_cents': _aggregate(buckets[(m, reg)], agg)} for m, reg in keys]


def lookup(rows, lookup, request):
    prepared = revenue(rows, lookup, request)
    targets = {item.get('region'): item.get('target') for item in lookup}
    for r in prepared:
        target = targets.get(r.get('region'))
        val = r.get('revenue_cents')
        r['revenue_cents_per_target'] = val / target if val is not None and target not in (None, 0) else None
    return prepared


def window(rows, lookup, request):
    prepared = _prepare(rows, request)
    width = request.get('window', 2)
    if width not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    values = []
    for i, r in enumerate(prepared):
        values.append(r.get('revenue_cents'))
        sample = [x for x in values[max(0, i-width+1):i+1] if x is not None]
        r['roll_revenue_cents'] = mean(sample) if sample else None
    return prepared


CHECKS = {'clean': clean, 'revenue': revenue, 'group': group, 'monthly': monthly, 'lookup': lookup, 'window': window}
