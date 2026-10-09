"""Native implementations of the tabular publication service families."""
from statistics import median


def _filled(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero' or not vals:
        replacement = 0
    elif mode == 'mean':
        replacement = sum(vals) / len(vals)
    elif mode == 'median':
        replacement = median(vals)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [replacement if r.get('units') is None else r.get('units') for r in rows]


def _revenue_rows(rows, units=None):
    out = []
    for i, row in enumerate(rows):
        r = dict(row)
        if units is not None:
            r['units'] = units[i]
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
        out.append(r)
    return out


def clean(rows, lookup, request):
    units = _filled(rows, request)
    out = []
    for row, unit in zip(rows, units):
        r = dict(row)
        r['units'] = unit
        r['region'] = None if row.get('region') is None else row['region'].strip().lower()
        out.append(r)
    return out


def revenue(rows, lookup, request):
    return _revenue_rows(rows, _filled(rows, request))


def _normalized_revenues(rows, request):
    out = _revenue_rows(rows, _filled(rows, request))
    for r in out:
        r['region'] = None if r.get('region') is None else r['region'].strip().lower()
    return out


def _aggregate(vals, agg):
    present = [v for v in vals if v is not None]
    if agg == 'sum':
        return sum(present)
    if agg == 'count':
        return len(present)
    if agg == 'mean':
        return sum(present) / len(present) if present else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    groups = {}
    for r in _normalized_revenues(rows, request):
        key = r.get('region')
        if key is not None:
            groups.setdefault(key, []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'region': key, agg + '_revenue_cents': _aggregate(groups[key], agg)}
            for key in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    groups = {}
    for r in _normalized_revenues(rows, request):
        date, region = r.get('date'), r.get('region')
        month = None if date is None else date[:7]
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r['revenue_cents'])
    agg = request.get('agg', 'sum')
    return [{'month': month, 'region': region,
             agg + '_revenue_cents': _aggregate(groups[(month, region)], agg)}
            for month, region in sorted(groups, key=lambda k: (str(k[0]), str(k[1])))]


def lookup(rows, lookup, request):
    out = _normalized_revenues(rows, request)
    targets = {None if r.get('region') is None else r['region'].strip().lower(): r.get('target') for r in lookup}
    for r in out:
        target = targets.get(r.get('region'))
        value = r['revenue_cents']
        r['revenue_cents_per_target'] = (None if target is None or target == 0 or value is None
                                          else value / target)
    return out


def window(rows, lookup, request):
    out = _revenue_rows(rows, _filled(rows, request))
    width = request.get('window')
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1]
                if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
