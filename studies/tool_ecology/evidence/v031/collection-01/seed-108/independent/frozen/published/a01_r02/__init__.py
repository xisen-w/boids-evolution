"""Native implementations of the recurring table service families."""
from statistics import median

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']


def _norm(x):
    return x.strip().lower() if isinstance(x, str) else x


def _filled(rows, request):
    """Copy rows and apply the requested units imputation."""
    out = [dict(r) for r in rows]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if not vals:
        fill = 0
    elif mode == 'mean':
        fill = sum(vals) / len(vals)
    elif mode == 'median':
        fill = median(vals)
    else:
        fill = 0
    for r in out:
        r['region'] = _norm(r.get('region'))
        if r.get('units') is None:
            r['units'] = fill
    return out


def clean(rows, lookup, request):
    """Normalize region and impute units; retain input fields and row order."""
    return _filled(rows, request)


def _with_revenue(rows, request, normalize=True):
    out = [dict(r) for r in rows]
    vals = [r.get('units') for r in out if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    fill = 0 if not vals or mode not in ('mean', 'median') else (sum(vals) / len(vals) if mode == 'mean' else median(vals))
    for r in out:
        if normalize:
            r['region'] = _norm(r.get('region'))
        if r.get('units') is None:
            r['units'] = fill
    for r in out:
        units, price = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if units is None or price is None else units * price
    return out


def revenue(rows, lookup, request):
    """Return copied rows with normalized region, imputed units and revenue."""
    return _with_revenue(rows, request, normalize=False)


def _aggregate(values, agg):
    vals = [v for v in values if v is not None]
    if agg == 'count':
        return len(vals)
    if agg == 'mean':
        return sum(vals) / len(vals) if vals else None
    return sum(vals) if vals else 0


def group(rows, lookup, request):
    """Group revenues by normalized region; omit missing regions."""
    agg = request.get('agg', 'sum')
    groups = {}
    for r in _with_revenue(rows, request):
        key = r.get('region')
        if key is not None:
            groups.setdefault(key, []).append(r['revenue_cents'])
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(groups[k], agg)}
            for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    """Group by date month and normalized region, omitting missing keys."""
    agg = request.get('agg', 'sum')
    groups = {}
    for r in _with_revenue(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r['revenue_cents'])
    keys = sorted(groups, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': reg, f'{agg}_revenue_cents': _aggregate(groups[(m, reg)], agg)}
            for m, reg in keys]


def lookup(rows, lookup, request):
    """Append revenue-per-target using a normalized exact region lookup."""
    out = _with_revenue(rows, request)
    targets = {_norm(x.get('region')): x.get('target') for x in lookup}
    for r in out:
        target = targets.get(r.get('region'))
        rev = r['revenue_cents']
        r['revenue_cents_per_target'] = rev / target if rev is not None and target not in (None, 0) else None
    return out


def window(rows, lookup, request):
    """Append trailing ROWS mean revenue, including the current row."""
    out = _with_revenue(rows, request, normalize=False)
    width = request.get('window', 2)
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
