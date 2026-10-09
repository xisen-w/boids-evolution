"""Reusable table transformations for the six publication service families."""
from collections import defaultdict
from statistics import mean, median


def _filled(rows, request):
    """Return copied rows with normalized region and filled units."""
    fill = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = {'zero': 0, 'mean': (mean(vals) if vals else 0), 'median': (median(vals) if vals else 0)}.get(fill)
    if replacement is None:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    result = []
    for row in rows:
        out = dict(row)
        region = out.get('region')
        out['region'] = region.strip().lower() if isinstance(region, str) else region
        if out.get('units') is None:
            out['units'] = replacement
        result.append(out)
    return result


def clean(rows, lookup, request):
    """Normalize region and fill missing units; preserve every other field."""
    return _filled(rows, request)


def _revenue(rows, request):
    result = _filled(rows, request)
    for out in result:
        units, price = out.get('units'), out.get('price_cents')
        out['revenue_cents'] = None if units is None or price is None else units * price
    return result


def revenue(rows, lookup, request):
    """Fill units and derive revenue_cents."""
    return _revenue(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(present)
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return sum(present) / len(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def _groups(rows, keys, agg):
    grouped = defaultdict(list)
    for row in rows:
        key = tuple(row.get(k) for k in keys)
        if any(v is None for v in key):
            continue
        grouped[key].append(row.get('revenue_cents'))
    out = []
    for key, values in grouped.items():
        item = dict(zip(keys, key))
        item[agg + '_revenue_cents'] = _aggregate(values, agg)
        out.append(item)
    out.sort(key=lambda item: tuple(str(item[k]) for k in keys))
    return out


def group(rows, lookup, request):
    """Group normalized-region revenues using requested sum, mean, or count."""
    agg = request.get('agg', 'sum')
    return _groups(_revenue(rows, request), ('region',), agg)


def monthly(rows, lookup, request):
    """Group revenues by YYYY-MM month and normalized region."""
    agg = request.get('agg', 'sum')
    enriched = _revenue(rows, request)
    for row in enriched:
        date = row.get('date')
        row['month'] = date[:7] if date is not None else None
    return _groups(enriched, ('month', 'region'), agg)


def lookup(rows, lookup, request):
    """Add revenue per target using normalized exact region keys."""
    enriched = _revenue(rows, request)
    targets = {}
    for item in lookup:
        region = item.get('region')
        key = region.strip().lower() if isinstance(region, str) else region
        targets[key] = item.get('target')
    for row in enriched:
        target = targets.get(row.get('region'))
        value = row['revenue_cents']
        row['revenue_cents_per_target'] = (value / target
            if value is not None and target is not None and target != 0 else None)
    return enriched


def window(rows, lookup, request):
    """Add trailing ROWS rolling mean of nonmissing revenues."""
    enriched = _revenue(rows, request)
    size = request.get('window', 2)
    if size not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    vals = []
    for i, row in enumerate(enriched):
        vals.append(row.get('revenue_cents'))
        present = [v for v in vals[max(0, i-size+1):i+1] if v is not None]
        row['roll_revenue_cents'] = sum(present) / len(present) if present else None
    return enriched
