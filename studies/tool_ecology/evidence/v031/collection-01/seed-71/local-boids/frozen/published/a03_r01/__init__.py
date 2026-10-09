"""Native implementations of the recurring row-table service families."""
from statistics import mean, median


def _filled_units(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    method = request.get('fill', 'zero')
    if method == 'zero' or not vals:
        replacement = 0
    elif method == 'mean':
        replacement = mean(vals)
    elif method == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [replacement if r.get('units') is None else r.get('units') for r in rows]


def _base(rows, request):
    units = _filled_units(rows, request)
    result = []
    for row, unit in zip(rows, units):
        out = dict(row)
        if 'units' in row or unit is not None:
            out['units'] = unit
        region = row.get('region')
        if region is not None:
            out['region'] = region.strip().lower()
        price = row.get('price_cents')
        out['revenue_cents'] = None if unit is None or price is None else unit * price
        result.append(out)
    return result


def clean(rows, lookup, request):
    """Normalize region and fill units; preserve all row columns and order."""
    units = _filled_units(rows, request)
    out = []
    for row, unit in zip(rows, units):
        item = dict(row)
        if 'units' in row or unit is not None:
            item['units'] = unit
        if row.get('region') is not None:
            item['region'] = row['region'].strip().lower()
        out.append(item)
    return out


def revenue(rows, lookup, request):
    """Fill units and append revenue_cents (None when an operand is missing)."""
    return _base(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(present)
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return sum(present) / len(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    """Return region-level revenue aggregate, excluding missing regions."""
    data = _base(rows, request)
    groups = {}
    for row in data:
        key = row.get('region')
        if key is not None:
            groups.setdefault(key, []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': key, agg + '_revenue_cents': _aggregate(groups[key], agg)}
            for key in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    """Return month/region revenue aggregates; omit rows missing either key."""
    data = _base(rows, request)
    groups = {}
    for row in data:
        date = row.get('date')
        region = row.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(row['revenue_cents'])
    agg = request.get('agg', 'sum')
    keys = sorted(groups, key=lambda pair: (str(pair[0]), str(pair[1])))
    return [{'month': m, 'region': r, agg + '_revenue_cents': _aggregate(groups[(m, r)], agg)} for m, r in keys]


def lookup(rows, lookup, request):
    """Append revenue_cents_per_target using normalized exact region matching."""
    targets = {}
    for entry in lookup:
        region = entry.get('region')
        if region is not None:
            targets[region.strip().lower()] = entry.get('target')
    out = _base(rows, request)
    for row in out:
        target = targets.get(row.get('region'))
        rev = row['revenue_cents']
        row['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
    return out


def window(rows, lookup, request):
    """Append trailing-row mean of nonmissing revenue, including current row."""
    out = _base(rows, request)
    width = request.get('window', 2)
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for i, row in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
