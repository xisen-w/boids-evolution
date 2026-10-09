"""Reusable row-table services for cleaning, revenue, aggregation and windows."""
from statistics import median


def _copy_rows(rows):
    return [dict(row) for row in rows]


def _fill(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if method == 'zero': value = 0
    elif not vals: value = 0
    elif method == 'mean': value = sum(vals) / len(vals)
    elif method == 'median': value = median(vals)
    else: raise ValueError("fill must be 'zero', 'mean', or 'median'")
    for r in rows:
        if r.get('units') is None: r['units'] = value
    return rows


def clean(rows, lookup=None, request=None):
    request = request or {}
    out = _copy_rows(rows)
    _fill(out, request.get('fill', 'zero'))
    for r in out:
        if r.get('region') is not None: r['region'] = r['region'].strip().lower()
    return out


def _revenue(rows, request):
    out = _copy_rows(rows)
    _fill(out, request.get('fill', 'zero'))
    for r in out:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def revenue(rows, lookup=None, request=None):
    return _revenue(rows, request or {})


def _agg(values, kind):
    if kind == 'sum': return sum(values)
    if kind == 'count': return len(values)
    if kind == 'mean': return sum(values) / len(values) if values else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup=None, request=None):
    req = request or {}
    kind = req.get('agg', 'sum')
    data = _revenue(rows, req)
    groups = {}
    for r in data:
        region = r.get('region')
        if region is None: continue
        key = region.strip().lower()
        groups.setdefault(key, []).append(r.get('revenue_cents'))
    return [{'region': key, kind + '_revenue_cents': _agg([x for x in vals if x is not None], kind)}
            for key, vals in sorted(groups.items(), key=lambda item: str(item[0]))]


def monthly(rows, lookup=None, request=None):
    req = request or {}
    kind = req.get('agg', 'sum')
    data = _revenue(rows, req)
    groups = {}
    for r in data:
        region = r.get('region')
        date = r.get('date')
        month = date[:7] if date is not None else None
        if region is None or month is None: continue
        key = (month, region.strip().lower())
        groups.setdefault(key, []).append(r.get('revenue_cents'))
    return [{'month': m, 'region': reg, kind + '_revenue_cents': _agg([x for x in vals if x is not None], kind)}
            for (m, reg), vals in sorted(groups.items(), key=lambda item: (str(item[0][0]), str(item[0][1])))]


def lookup(rows, lookup, request=None):
    data = _revenue(rows, request or {})
    targets = {
        (r.get('region').strip().lower() if r.get('region') is not None else None): r.get('target')
        for r in lookup
    }
    for r in data:
        region = r.get('region')
        key = region.strip().lower() if region is not None else None
        if region is not None:
            r['region'] = key
        target = targets.get(key)
        rev = r.get('revenue_cents')
        r['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return data


def window(rows, lookup=None, request=None):
    req = request or {}
    width = req.get('window', 2)
    if width not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    data = _revenue(rows, req)
    for i, r in enumerate(data):
        vals = [x['revenue_cents'] for x in data[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return data


# Explicit service adapters (all public service functions share the required signature).
clean_service = clean
revenue_service = revenue
group_service = group
monthly_service = monthly
lookup_service = lookup
window_service = window
