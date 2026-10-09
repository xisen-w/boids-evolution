"""Native implementations of tabular service families."""
from statistics import mean, median

_MISSING = object()

def _base(rows, request):
    """Copy input rows and normalize/fill/derive revenue without mutation."""
    fill = request.get('fill', 'zero')
    present = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero' or not present:
        replacement = 0
    elif fill == 'mean':
        replacement = mean(present)
    elif fill == 'median':
        replacement = median(present)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out = []
    for source in rows:
        r = dict(source)
        region = r.get('region')
        r['region'] = region.strip().lower() if isinstance(region, str) else region
        units = r.get('units')
        if units is None:
            units = replacement
            r['units'] = units
        price = r.get('price_cents')
        r['revenue_cents'] = None if units is None or price is None else units * price
        out.append(r)
    return out

def _filled(rows, request):
    fill = request.get('fill', 'zero')
    present = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero' or not present: replacement = 0
    elif fill == 'mean': replacement = mean(present)
    elif fill == 'median': replacement = median(present)
    else: raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out = []
    for source in rows:
        r = dict(source)
        region = r.get('region')
        r['region'] = region.strip().lower() if isinstance(region, str) else region
        if r.get('units') is None: r['units'] = replacement
        out.append(r)
    return out

def _filled_without_normalizing(rows, request):
    fill = request.get('fill', 'zero')
    present = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero' or not present: replacement = 0
    elif fill == 'mean': replacement = mean(present)
    elif fill == 'median': replacement = median(present)
    else: raise ValueError("fill must be 'zero', 'mean', or 'median'")
    result = []
    for source in rows:
        row = dict(source)
        if row.get('units') is None: row['units'] = replacement
        result.append(row)
    return result

def clean(rows, lookup, request):
    return _filled(rows, request)

def revenue(rows, lookup, request):
    data = []
    for source in _filled_without_normalizing(rows, request):
        u, p = source.get('units'), source.get('price_cents')
        source['revenue_cents'] = None if u is None or p is None else u * p
        data.append(source)
    return data

def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals) / len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")

def group(rows, lookup, request):
    data = _base(rows, request)
    agg = request.get('agg', 'sum')
    groups = {}
    for r in data:
        key = r.get('region')
        if key is not None: groups.setdefault(key, []).append(r['revenue_cents'])
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(v, agg)} for k,v in sorted(groups.items(), key=lambda kv: str(kv[0]))]

def monthly(rows, lookup, request):
    data = _base(rows, request)
    agg = request.get('agg', 'sum')
    groups = {}
    for r in data:
        month = r.get('date')
        month = month[:7] if month is not None else None
        region = r.get('region')
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r['revenue_cents'])
    return [{'month': m, 'region': reg, f'{agg}_revenue_cents': _aggregate(v, agg)}
            for (m,reg),v in sorted(groups.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1])))]

def lookup(rows, lookup, request):
    data = _base(rows, request)
    targets = {}
    for item in lookup:
        key = item.get('region')
        if isinstance(key, str): key = key.strip().lower()
        targets[key] = item.get('target')
    for r in data:
        target = targets.get(r.get('region'))
        revenue_value = r['revenue_cents']
        r['revenue_cents_per_target'] = None if target is None or target == 0 or revenue_value is None else revenue_value / target
    return data

def window(rows, lookup, request):
    data = revenue(rows, lookup, request)
    width = request.get('window')
    if width not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    revenues = []
    for i,r in enumerate(data):
        revenues.append(r['revenue_cents'])
        vals = [v for v in revenues[max(0, i-width+1):i+1] if v is not None]
        r['roll_revenue_cents'] = sum(vals)/len(vals) if vals else None
    return data
