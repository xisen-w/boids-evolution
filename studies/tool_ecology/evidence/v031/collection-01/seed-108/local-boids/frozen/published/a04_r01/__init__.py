"""Native implementations of the recurring tabular service families."""
from copy import deepcopy


def _fill_units(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if method == 'zero' or not vals:
        value = 0
    elif method == 'mean':
        value = sum(vals) / len(vals)
    elif method == 'median':
        s = sorted(vals); n = len(s)
        value = s[n // 2] if n % 2 else (s[n//2-1] + s[n//2]) / 2
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [value if r.get('units') is None else r.get('units') for r in rows]


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _base(rows, request):
    units = _fill_units(rows, request.get('fill'))
    out = []
    for row, unit in zip(rows, units):
        r = dict(row)
        r['region'] = _region(r.get('region'))
        r['units'] = unit
        price = r.get('price_cents')
        r['revenue_cents'] = None if unit is None or price is None else unit * price
        out.append(r)
    return out


def clean(rows, lookup, request):
    result = []
    for row, unit in zip(rows, _fill_units(rows, request.get('fill'))):
        r = dict(row); r['region'] = _region(r.get('region')); r['units'] = unit
        result.append(r)
    return result


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals) / len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def _group_output(records, keys, agg):
    buckets = {}
    for r in records:
        key = tuple(r.get(k) for k in keys)
        if any(v is None for v in key): continue
        buckets.setdefault(key, []).append(r['revenue_cents'])
    def sortkey(key): return tuple(str(x) for x in key)
    out = []
    for key in sorted(buckets, key=sortkey):
        row = dict(zip(keys, key)); row[agg + '_revenue_cents'] = _aggregate(buckets[key], agg); out.append(row)
    return out


def group(rows, lookup, request):
    records = _base(rows, request)
    return _group_output(records, ['region'], request.get('agg'))


def monthly(rows, lookup, request):
    records = _base(rows, request)
    for r in records:
        date = r.get('date')
        r['month'] = date[:7] if date is not None else None
    return _group_output(records, ['month', 'region'], request.get('agg'))


def lookup(rows, lookup, request):
    records = _base(rows, request)
    targets = { _region(x.get('region')): x.get('target') for x in lookup }
    for r in records:
        target = targets.get(r.get('region'))
        rev = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if rev is None or target is None or target == 0 else rev / target
    return records


def window(rows, lookup, request):
    records = _base(rows, request)
    size = request.get('window')
    if size not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(records):
        vals = [x['revenue_cents'] for x in records[max(0, i-size+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return records
