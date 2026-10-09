"""Native implementations of the six table service families."""
from statistics import median


def _units(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'mean': value = sum(vals) / len(vals) if vals else 0
    elif mode == 'median': value = median(vals) if vals else 0
    else: value = 0
    return [dict(r, units=(r.get('units') if r.get('units') is not None else value)) for r in rows]


def clean(rows, lookup, request):
    out = _units(rows, request)
    for r in out:
        if r.get('region') is not None: r['region'] = r['region'].strip().lower()
    return out


def _revenue(rows, request):
    out = _units(rows, request)
    for r in out:
        a, b = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if a is None or b is None else a * b
    return out


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals) / len(vals) if vals else None
    return sum(vals) if vals else 0


def _group(rows, request, monthly=False):
    data = _revenue(rows, request)
    groups = {}
    for r in data:
        region = r.get('region')
        if region is not None: region = region.strip().lower()
        month = r.get('date')[:7] if r.get('date') is not None else None
        keys = (month, region) if monthly else (region,)
        if any(k is None for k in keys): continue
        groups.setdefault(keys, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    result = []
    for keys in sorted(groups, key=lambda x: tuple(str(k) for k in x)):
        item = {'month': keys[0], 'region': keys[1]} if monthly else {'region': keys[0]}
        item[agg + '_revenue_cents'] = _aggregate(groups[keys], agg)
        result.append(item)
    return result


def group(rows, lookup, request):
    return _group(rows, request)


def monthly(rows, lookup, request):
    return _group(rows, request, True)


def lookup(rows, lookup, request):
    out = _revenue(rows, request)
    targets = {}
    for item in lookup:
        key = item.get('region')
        if key is not None: key = key.strip().lower()
        targets[key] = item.get('target')
    for r in out:
        region = r.get('region')
        if region is not None: region = region.strip().lower()
        target = targets.get(region)
        rev = r['revenue_cents']
        r['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return out


def window(rows, lookup, request):
    out = _revenue(rows, request)
    width = request.get('window', 2)
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals)/len(vals) if vals else None
    return out
