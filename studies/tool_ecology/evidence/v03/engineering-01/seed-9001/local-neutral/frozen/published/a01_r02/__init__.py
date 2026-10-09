"""Native adapters for the six table service families."""
from statistics import mean, median


def _filled(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    replacement = 0 if not vals else (mean(vals) if mode == 'mean' else median(vals) if mode == 'median' else 0)
    return [dict(r, units=(replacement if r.get('units') is None else r.get('units'))) for r in rows]


def _base(rows, request, normalize=True):
    out = _filled(rows, request)
    for r in out:
        if normalize and r.get('region') is not None:
            r['region'] = r['region'].strip().lower()
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    out = _filled(rows, request)
    for r in out:
        if r.get('region') is not None: r['region'] = r['region'].strip().lower()
    return out


def revenue(rows, lookup, request):
    return _base(rows, request, False)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'count': return len(present)
    if agg == 'mean': return sum(present) / len(present) if present else None
    return sum(present) if present else 0


def group(rows, lookup, request):
    data = _base(rows, request)
    groups = {}
    for r in data:
        key = r.get('region')
        if key is not None: groups.setdefault(key, []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    data = _base(rows, request)
    groups = {}
    for r in data:
        region = r.get('region')
        date = r.get('date')
        month = date[:7] if date is not None else None
        if region is not None and month is not None:
            groups.setdefault((month, region), []).append(r.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(groups[(m, r)], agg)}
            for m, r in sorted(groups, key=lambda k: (str(k[0]), str(k[1])))]


def lookup(rows, lookup, request):
    data = _base(rows, request)
    targets = {
        (r.get('region').strip().lower() if r.get('region') is not None else None): r.get('target')
        for r in lookup
    }
    for r in data:
        target = targets.get(r.get('region'))
        value = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if value is None or target in (None, 0) else value / target
    return data


def window(rows, lookup, request):
    data = _base(rows, request, False)
    width = request.get('window', 2)
    history = []
    for r in data:
        history.append(r.get('revenue_cents'))
        vals = [v for v in history[-width:] if v is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return data
