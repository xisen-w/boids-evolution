"""Reusable row-oriented implementations of the publication service families."""
from statistics import median

_MISSING = object()

def _filled_rows(rows, request):
    """Copy records, normalize regions, and impute units without mutating input."""
    fill = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero' or not vals:
        replacement = 0
    elif fill == 'mean':
        replacement = sum(vals) / len(vals)
    elif fill == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out = []
    for row in rows:
        r = dict(row)
        region = r.get('region')
        r['region'] = region.strip().lower() if isinstance(region, str) else region
        if r.get('units') is None:
            r['units'] = replacement
        out.append(r)
    return out

def clean(rows, lookup, request):
    """Normalize region and impute units; preserve all fields and row order."""
    return _filled_rows(rows, request)

def _with_revenue(rows, request):
    result = _filled_rows(rows, request)
    for r in result:
        units, price = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if units is None or price is None else units * price
    return result

def revenue(rows, lookup, request):
    """Return copied, normalized/imputed rows with revenue_cents appended."""
    return _with_revenue(rows, request)

def _aggregate(values, agg):
    values = [x for x in values if x is not None]
    if agg == 'sum': return sum(values)
    if agg == 'count': return len(values)
    if agg == 'mean': return sum(values) / len(values) if values else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")

def group(rows, lookup, request):
    """Aggregate nonmissing revenue by normalized, nonmissing region."""
    groups = {}
    for r in _with_revenue(rows, request):
        key = r.get('region')
        if key is not None:
            groups.setdefault(key, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    col = agg + '_revenue_cents'
    return [{'region': k, col: _aggregate(groups[k], agg)}
            for k in sorted(groups, key=str)]

def monthly(rows, lookup, request):
    """Aggregate by month and normalized region, omitting incomplete keys."""
    groups = {}
    for r in _with_revenue(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    col = agg + '_revenue_cents'
    keys = sorted(groups, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': r, col: _aggregate(groups[(m, r)], agg)} for m, r in keys]

def lookup(rows, lookup, request):
    """Append revenue_cents_per_target using normalized region-key targets."""
    targets = {}
    for item in lookup:
        key = item.get('region')
        key = key.strip().lower() if isinstance(key, str) else key
        targets[key] = item.get('target')
    result = _with_revenue(rows, request)
    for r in result:
        revenue_value = r['revenue_cents']
        target = targets.get(r.get('region'))
        r['revenue_cents_per_target'] = (revenue_value / target
            if revenue_value is not None and target is not None and target != 0 else None)
    return result

def window(rows, lookup, request):
    """Append trailing-row (including current row) nonmissing revenue means."""
    result = _with_revenue(rows, request)
    width = request.get('window', 2)
    if not isinstance(width, int) or width <= 0:
        raise ValueError('window must be a positive integer')
    revenues = [r['revenue_cents'] for r in result]
    for i, r in enumerate(result):
        vals = [v for v in revenues[max(0, i-width+1):i+1] if v is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return result

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
