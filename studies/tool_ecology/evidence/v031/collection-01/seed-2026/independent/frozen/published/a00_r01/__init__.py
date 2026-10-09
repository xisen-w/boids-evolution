"""Native implementations of the tabular publication service families."""
from collections import defaultdict


def _filled_units(rows, request):
    values = [r.get('units') for r in rows]
    missing = [v for v in values if v is None]
    if not missing:
        return values
    method = request.get('fill', 'zero')
    known = sorted(v for v in values if v is not None)
    if method == 'zero' or not known:
        replacement = 0
    elif method == 'mean':
        replacement = sum(known) / len(known)
    elif method == 'median':
        n = len(known)
        replacement = known[n // 2] if n % 2 else (known[n // 2 - 1] + known[n // 2]) / 2
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [replacement if v is None else v for v in values]


def _regions(rows, normalize):
    return [(r.get('region').strip().lower() if normalize and r.get('region') is not None else r.get('region')) for r in rows]


def _revenue_rows(rows, request, normalize=False):
    units = _filled_units(rows, request)
    regions = _regions(rows, normalize)
    out = []
    for row, unit, region in zip(rows, units, regions):
        item = dict(row)
        if normalize:
            item['region'] = region
        price = row.get('price_cents')
        item['units'] = unit
        item['revenue_cents'] = None if unit is None or price is None else unit * price
        out.append(item)
    return out


def clean(rows, lookup, request):
    units = _filled_units(rows, request)
    out = []
    for row, unit, region in zip(rows, units, _regions(rows, True)):
        item = dict(row)
        item['region'] = region
        item['units'] = unit
        out.append(item)
    return out


def revenue(rows, lookup, request):
    return _revenue_rows(rows, request)


def _aggregate(values, agg):
    present = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(present)
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return sum(present) / len(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def _group(rows, request, monthly):
    enriched = _revenue_rows(rows, request, normalize=True)
    buckets = defaultdict(list)
    for row in enriched:
        region = row.get('region')
        month = row.get('date')[:7] if row.get('date') is not None else None
        if region is None or (monthly and month is None):
            continue
        key = (month, region) if monthly else (region,)
        buckets[key].append(row.get('revenue_cents'))
    agg = request.get('agg', 'sum')
    keys = sorted(buckets, key=lambda k: tuple(str(part) for part in k))
    result = []
    for key in keys:
        item = {}
        if monthly:
            item['month'], item['region'] = key
        else:
            item['region'] = key[0]
        item[agg + '_revenue_cents'] = _aggregate(buckets[key], agg)
        result.append(item)
    return result


def group(rows, lookup, request):
    return _group(rows, request, False)


def monthly(rows, lookup, request):
    return _group(rows, request, True)


def lookup(rows, lookup, request):
    enriched = _revenue_rows(rows, request, normalize=True)
    targets = {item.get('region'): item.get('target') for item in lookup}
    for item in enriched:
        target = targets.get(item.get('region'))
        value = item.get('revenue_cents')
        item['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value / target
    return enriched


def window(rows, lookup, request):
    enriched = _revenue_rows(rows, request)
    width = request.get('window')
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for index, item in enumerate(enriched):
        values = [r['revenue_cents'] for r in enriched[max(0, index-width+1):index+1] if r['revenue_cents'] is not None]
        item['roll_revenue_cents'] = sum(values) / len(values) if values else None
    return enriched
