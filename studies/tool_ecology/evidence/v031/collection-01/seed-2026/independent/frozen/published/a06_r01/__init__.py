"""Native dataframe-like services for the publication service families."""
from statistics import median

_MISSING = object()

def _base(rows, request):
    """Copy rows, normalize region, fill units and derive revenue."""
    out = [dict(row) for row in rows]
    missing = [r.get('units') is None for r in out]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero': replacement = 0
    elif mode == 'mean': replacement = sum(vals) / len(vals) if vals else 0
    elif mode == 'median': replacement = median(vals) if vals else 0
    else: raise ValueError("fill must be zero, mean, or median")
    for r, is_missing in zip(out, missing):
        region = r.get('region')
        r['region'] = region.strip().lower() if isinstance(region, str) else region
        if is_missing: r['units'] = replacement
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out

def clean(rows, lookup, request):
    out = [dict(r) for r in rows]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    replacement = 0 if mode == 'zero' or not vals else (sum(vals)/len(vals) if mode == 'mean' else median(vals) if mode == 'median' else None)
    if replacement is None: raise ValueError('fill must be zero, mean, or median')
    for r in out:
        if isinstance(r.get('region'), str): r['region'] = r['region'].strip().lower()
        if r.get('units') is None: r['units'] = replacement
    return out

def revenue(rows, lookup, request):
    return _base(rows, request)

def _aggregate(values, agg):
    valid = [v for v in values if v is not None]
    if agg == 'sum': return sum(valid)
    if agg == 'count': return len(valid)
    if agg == 'mean': return sum(valid)/len(valid) if valid else None
    raise ValueError('agg must be sum, mean, or count')

def group(rows, lookup, request):
    data = _base(rows, request); agg = request.get('agg', 'sum'); groups = {}
    for r in data:
        key = r.get('region')
        if key is not None: groups.setdefault(key, []).append(r['revenue_cents'])
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(v, agg)} for k,v in sorted(groups.items(), key=lambda kv: str(kv[0]))]

def monthly(rows, lookup, request):
    data = _base(rows, request); agg = request.get('agg', 'sum'); groups = {}
    for r in data:
        region = r.get('region'); date = r.get('date'); month = date[:7] if date is not None else None
        if region is not None and month is not None: groups.setdefault((month, region), []).append(r['revenue_cents'])
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(v, agg)} for (m,r),v in sorted(groups.items(), key=lambda kv:(str(kv[0][0]),str(kv[0][1])))]

def lookup(rows, lookup, request):
    data = _base(rows, request)
    targets = {item.get('region'): item.get('target') for item in lookup}
    for r in data:
        target = targets.get(r.get('region'), _MISSING); rev = r['revenue_cents']
        r['revenue_cents_per_target'] = None if target is _MISSING or target is None or target == 0 or rev is None else rev / target
    return data

def window(rows, lookup, request):
    data = _base(rows, request); width = request.get('window')
    if width not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(data):
        vals = [x['revenue_cents'] for x in data[max(0,i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals)/len(vals) if vals else None
    return data
