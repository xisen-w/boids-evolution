"""Native implementations of the recurring tabular service families."""
from statistics import mean, median


def _units(rows, fill):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero':
        replacement = 0
    elif fill == 'mean':
        replacement = mean(vals) if vals else 0
    elif fill == 'median':
        replacement = median(vals) if vals else 0
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [dict(r, units=(r.get('units') if r.get('units') is not None else replacement)) for r in rows]


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _base(rows, request):
    out = _units(rows, request.get('fill', 'zero'))
    for r in out:
        r['region'] = _region(r.get('region'))
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = u * p if u is not None and p is not None else None
    return out


def clean(rows, lookup, request):
    return [{**r, 'region': _region(r.get('region'))} for r in _units(rows, request.get('fill', 'zero'))]


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return mean(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    agg = request.get('agg', 'sum')
    groups = {}
    for r in _base(rows, request):
        k = r.get('region')
        if k is not None: groups.setdefault(k, []).append(r['revenue_cents'])
    name = agg + '_revenue_cents'
    return [{'region': k, name: _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    agg = request.get('agg', 'sum')
    groups = {}
    for r in _base(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r['revenue_cents'])
    name = agg + '_revenue_cents'
    return [{'month': m, 'region': r, name: _aggregate(groups[(m, r)], agg)}
            for m, r in sorted(groups, key=lambda k: (str(k[0]), str(k[1])))]


def lookup_service(rows, lookup_rows, request):
    out = _base(rows, request)
    targets = {_region(x.get('region')): x.get('target') for x in lookup_rows}
    for r in out:
        target, rev = targets.get(r.get('region')), r.get('revenue_cents')
        r['revenue_cents_per_target'] = rev / target if target not in (None, 0) and rev is not None else None
    return out


def window(rows, lookup, request):
    out = _base(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    revenues = []
    for i, r in enumerate(out):
        revenues.append(r['revenue_cents'])
        vals = [v for v in revenues[max(0, i-width+1):i+1] if v is not None]
        r['roll_revenue_cents'] = mean(vals) if vals else None
    return out

# Public service-adapter names used by publication checks.
lookup = lookup_service
