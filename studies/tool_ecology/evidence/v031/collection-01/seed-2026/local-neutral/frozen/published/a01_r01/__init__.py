"""Reusable implementations of the six tabular service families."""
from statistics import mean, median

_MISSING = object()

def _copy_rows(rows):
    return [dict(row) for row in rows]

def _filled(rows, request):
    out = _copy_rows(rows)
    vals = [r.get('units') for r in out if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    replacement = 0 if not vals else (mean(vals) if mode == 'mean' else median(vals) if mode == 'median' else 0)
    for r in out:
        if r.get('units') is None:
            r['units'] = replacement
    return out

def _base(rows, request, normalize=True):
    out = _filled(rows, request)
    for r in out:
        if normalize and r.get('region') is not None:
            r['region'] = r['region'].strip().lower()
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out

def clean(rows, lookup, request):
    return _base(rows, request, True)

def revenue(rows, lookup, request):
    return _base(rows, request, False)

def _aggregate(rows, request, keys):
    agg = request.get('agg', 'sum')
    groups = {}
    for r in rows:
        key = tuple(r.get(k) for k in keys)
        if any(v is None for v in key):
            continue
        groups.setdefault(key, []).append(r.get('revenue_cents'))
    result = []
    for key, values in groups.items():
        valid = [x for x in values if x is not None]
        value = (sum(valid) if valid else 0) if agg == 'sum' else (len(valid) if agg == 'count' else (sum(valid)/len(valid) if valid else None))
        row = dict(zip(keys, key)); row[agg + '_revenue_cents'] = value; result.append(row)
    result.sort(key=lambda r: tuple(str(r[k]) for k in keys))
    return result

def group(rows, lookup, request):
    return _aggregate(_base(rows, request), request, ['region'])

def monthly(rows, lookup, request):
    out = _base(rows, request)
    for r in out:
        d = r.get('date')
        r['month'] = d[:7] if d is not None else None
    return _aggregate(out, request, ['month', 'region'])

def lookup(rows, lookup, request):
    out = _base(rows, request)
    targets = {}
    for item in lookup or []:
        reg = item.get('region')
        if reg is not None:
            targets[reg.strip().lower()] = item.get('target')
    for r in out:
        target = targets.get(r.get('region'), _MISSING)
        rev = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target is _MISSING or target is None or target == 0 or rev is None else rev / target
    return out

def window(rows, lookup, request):
    out = _base(rows, request, False)
    width = request.get('window', 2)
    for i, r in enumerate(out):
        vals = [x.get('revenue_cents') for x in out[max(0, i-width+1):i+1] if x.get('revenue_cents') is not None]
        r['roll_revenue_cents'] = sum(vals)/len(vals) if vals else None
    return out
