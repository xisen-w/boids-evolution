"""Reusable row-oriented implementations of the publication service families."""
from statistics import mean, median


def _filled(rows, request):
    mode = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero' or not vals:
        replacement = 0
    elif mode == 'mean':
        replacement = mean(vals)
    elif mode == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out = []
    for row in rows:
        item = dict(row)
        if item.get('units') is None:
            item['units'] = replacement
        out.append(item)
    return out


def _base(rows, request):
    out = _filled(rows, request)
    for r in out:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def _region(r):
    val = r.get('region')
    r['region'] = val.strip().lower() if isinstance(val, str) else val


def clean(rows, lookup, request):
    out = _filled(rows, request)
    for r in out:
        _region(r)
    return out


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(present)
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return sum(present) / len(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    data = _base(rows, request)
    buckets = {}
    for r in data:
        _region(r)
        key = r.get('region')
        if key is not None:
            buckets.setdefault(key, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': key, agg + '_revenue_cents': _aggregate(buckets[key], agg)}
            for key in sorted(buckets, key=str)]


def monthly(rows, lookup, request):
    data = _base(rows, request)
    buckets = {}
    for r in data:
        _region(r)
        date = r.get('date')
        month = date[:7] if date is not None else None
        key = (month, r.get('region'))
        if None not in key:
            buckets.setdefault(key, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': reg, agg + '_revenue_cents': _aggregate(buckets[(m, reg)], agg)}
            for m, reg in sorted(buckets, key=lambda k: (str(k[0]), str(k[1])))]


def lookup(rows, lookup, request):
    data = _base(rows, request)
    targets = {r.get('region'): r.get('target') for r in lookup}
    for r in data:
        _region(r)
        target = targets.get(r.get('region'))
        rev = r['revenue_cents']
        r['revenue_cents_per_target'] = None if target in (None, 0) or rev is None else rev / target
    return data


def window(rows, lookup, request):
    data = _base(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    vals = []
    for i, r in enumerate(data):
        vals.append(r['revenue_cents'])
        recent = [v for v in vals[max(0, i-width+1):i+1] if v is not None]
        r['roll_revenue_cents'] = sum(recent) / len(recent) if recent else None
    return data
