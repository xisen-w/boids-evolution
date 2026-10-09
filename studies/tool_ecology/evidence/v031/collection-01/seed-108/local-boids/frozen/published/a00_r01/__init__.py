"""Native adapters for tabular data service families."""
from statistics import mean, median

_MISSING = object()

def _filled(rows, request):
    vals = [r.get('units') for r in rows]
    missing = [v for v in vals if v is None]
    mode = request.get('fill', 'zero')
    if not missing:
        fill = 0
    elif mode == 'zero':
        fill = 0
    elif mode in ('mean', 'median'):
        present = [v for v in vals if v is not None]
        fill = (mean(present) if mode == 'mean' else median(present)) if present else 0
    else:
        raise ValueError("fill must be zero, mean, or median")
    return [fill if v is None else v for v in vals]

def _derived(rows, request):
    units = _filled(rows, request)
    result = []
    for row, unit in zip(rows, units):
        out = dict(row)
        price = row.get('price_cents')
        out['units'] = unit
        out['revenue_cents'] = None if unit is None or price is None else unit * price
        result.append(out)
    return result

def clean(rows, lookup, request):
    units = _filled(rows, request)
    out = []
    for row, unit in zip(rows, units):
        item = dict(row); item['region'] = row.get('region').strip().lower() if isinstance(row.get('region'), str) else row.get('region'); item['units'] = unit
        out.append(item)
    return out

def revenue(rows, lookup, request):
    return _derived(rows, request)

def _agg(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum': return sum(present)
    if agg == 'count': return len(present)
    if agg == 'mean': return mean(present) if present else None
    raise ValueError("agg must be sum, mean, or count")

def _grouped(rows, request, monthly=False):
    derived = _derived(rows, request)
    groups = {}
    for row in derived:
        region = row.get('region')
        region = region.strip().lower() if isinstance(region, str) else region
        month = row.get('date')[:7] if row.get('date') is not None else None
        if region is None or (monthly and month is None): continue
        key = (month, region) if monthly else (region,)
        groups.setdefault(key, []).append(row.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    keys = sorted(groups, key=lambda k: tuple(str(x) for x in k))
    output = []
    for key in keys:
        record = {}
        if monthly: record['month'] = key[0]
        record['region'] = key[-1]
        record[agg + '_revenue_cents'] = _agg(groups[key], agg)
        output.append(record)
    return output

def group(rows, lookup, request):
    return _grouped(rows, request)

def monthly(rows, lookup, request):
    return _grouped(rows, request, True)

def lookup_service(rows, lookup, request):
    derived = _derived(rows, request)
    targets = {item.get('region'): item.get('target') for item in lookup}
    output = []
    for row in derived:
        region = row.get('region')
        region = region.strip().lower() if isinstance(region, str) else region
        # Lookup keys are exact; regions are normalized before matching.
        target = targets.get(region, _MISSING)
        revenue_value = row.get('revenue_cents')
        value = None if target is _MISSING or target is None or target == 0 or revenue_value is None else revenue_value / target
        item = dict(row); item['region'] = region; item['revenue_cents_per_target'] = value
        output.append(item)
    return output

def window(rows, lookup, request):
    derived = _derived(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    values = []
    result = []
    for i, row in enumerate(derived):
        values.append(row.get('revenue_cents'))
        trailing = values[max(0, i-width+1):i+1]
        present = [v for v in trailing if v is not None]
        item = dict(row); item['roll_revenue_cents'] = mean(present) if present else None
        result.append(item)
    return result

# Public adapter names (lookup_service avoids shadowing the argument concept).
lookup = lookup_service
