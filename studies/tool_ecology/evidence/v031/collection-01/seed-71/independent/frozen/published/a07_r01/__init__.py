"""Native implementations of the tabular service families."""
from collections import defaultdict
from statistics import median

_MISSING = object()

def _normalize(value):
    return value.strip().lower() if isinstance(value, str) else value

def _filled(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero' or not vals:
        fill = 0
    elif mode == 'mean':
        fill = sum(vals) / len(vals)
    elif mode == 'median':
        fill = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [fill if r.get('units') is None else r.get('units') for r in rows]

def _base(rows, request):
    units = _filled(rows, request.get('fill', 'zero'))
    result = []
    for row, unit in zip(rows, units):
        out = dict(row)
        out['region'] = _normalize(row.get('region'))
        out['units'] = unit
        price = row.get('price_cents')
        out['revenue_cents'] = None if unit is None or price is None else unit * price
        result.append(out)
    return result

def clean(rows, lookup, request):
    units = _filled(rows, request.get('fill', 'zero'))
    return [dict(r, region=_normalize(r.get('region')), units=u) for r,u in zip(rows,units)]

def revenue(rows, lookup, request):
    return _base(rows, request)

def _aggregate(vals, agg):
    vals = [v for v in vals if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")

def _groups(rows, request, monthly=False):
    agg = request.get('agg', 'sum')
    buckets = defaultdict(list)
    for row in _base(rows, request):
        region = row.get('region')
        month = row.get('date')
        month = month[:7] if month is not None else None
        if region is None or (monthly and month is None): continue
        key = (month, region) if monthly else (region,)
        buckets[key].append(row.get('revenue_cents'))
    keys = sorted(buckets, key=lambda k: tuple(str(x) for x in k))
    output = []
    for key in keys:
        val = _aggregate(buckets[key], agg)
        if monthly:
            output.append({'month': key[0], 'region': key[1], f'{agg}_revenue_cents': val})
        else:
            output.append({'region': key[0], f'{agg}_revenue_cents': val})
    return output

def group(rows, lookup, request):
    return _groups(rows, request)

def monthly(rows, lookup, request):
    return _groups(rows, request, True)

def lookup(rows, lookup, request):
    base = _base(rows, request)
    targets = {_normalize(item.get('region')): item.get('target') for item in lookup}
    output=[]
    for row in base:
        target=targets.get(row.get('region'))
        value=row.get('revenue_cents')
        row['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value/target
        output.append(row)
    return output

def window(rows, lookup, request):
    base = _base(rows, request)
    size=request.get('window', 2)
    if not isinstance(size, int) or size <= 0: raise ValueError('window must be a positive integer')
    for i,row in enumerate(base):
        vals=[r['revenue_cents'] for r in base[max(0,i-size+1):i+1] if r['revenue_cents'] is not None]
        row['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return base
