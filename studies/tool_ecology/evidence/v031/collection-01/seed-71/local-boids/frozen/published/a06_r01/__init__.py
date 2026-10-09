"""Native implementations of the recurring tabular service families."""
from collections import defaultdict


def _normalized(v):
    return v.strip().lower() if isinstance(v, str) else v


def _prepare(rows, request):
    copied = [dict(row) for row in rows]
    vals = [r.get('units') for r in copied if r.get('units') is not None]
    fill = request.get('fill', 'zero')
    if not vals:
        replacement = 0
    elif fill == 'zero':
        replacement = 0
    elif fill == 'mean':
        replacement = sum(vals) / len(vals)
    elif fill == 'median':
        s = sorted(vals)
        n = len(s)
        replacement = s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    for r in copied:
        r['region'] = _normalized(r.get('region'))
        if r.get('units') is None:
            r['units'] = replacement
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return copied


def clean(rows, lookup, request):
    out = [dict(row) for row in rows]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    fill = request.get('fill', 'zero')
    if not vals: value = 0
    elif fill == 'zero': value = 0
    elif fill == 'mean': value = sum(vals) / len(vals)
    elif fill == 'median':
        s = sorted(vals); n = len(s); value = s[n//2] if n % 2 else (s[n//2-1]+s[n//2])/2
    else: raise ValueError("fill must be 'zero', 'mean', or 'median'")
    for r in out:
        r['region'] = _normalized(r.get('region'))
        if r.get('units') is None: r['units'] = value
    return out


def revenue(rows, lookup, request):
    return _prepare(rows, request)


def _aggregate(values, agg):
    present = [x for x in values if x is not None]
    if agg == 'sum': return sum(present)
    if agg == 'count': return len(present)
    if agg == 'mean': return sum(present) / len(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    agg = request.get('agg', 'sum')
    buckets = defaultdict(list)
    for r in _prepare(rows, request):
        if r.get('region') is not None: buckets[r['region']].append(r['revenue_cents'])
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(buckets[k], agg)} for k in sorted(buckets, key=str)]


def monthly(rows, lookup, request):
    agg = request.get('agg', 'sum')
    buckets = defaultdict(list)
    for r in _prepare(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            buckets[(month, region)].append(r['revenue_cents'])
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(buckets[(m,r)], agg)}
            for m,r in sorted(buckets, key=lambda k: (str(k[0]), str(k[1])))]


def lookup(rows, lookup, request):
    out = _prepare(rows, request)
    targets = {_normalized(x.get('region')): x.get('target') for x in lookup if x.get('region') is not None}
    for r in out:
        target = targets.get(r.get('region'))
        value = r.get('revenue_cents')
        r['revenue_cents_per_target'] = value / target if value is not None and target not in (None, 0) else None
    return out


def window(rows, lookup, request):
    out = _prepare(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(out):
        values = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(values) / len(values) if values else None
    return out
