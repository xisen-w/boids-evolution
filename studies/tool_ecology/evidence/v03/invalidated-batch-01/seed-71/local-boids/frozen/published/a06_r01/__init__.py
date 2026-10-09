"""Native implementations of the tabular publication service families."""
from collections import defaultdict
from statistics import mean, median


def _filled(rows, fill):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = {'zero': 0, 'mean': mean, 'median': median}.get(fill, 0)
    value = replacement(vals) if callable(replacement) and vals else (0 if callable(replacement) else replacement)
    out = []
    for row in rows:
        r = dict(row)
        if r.get('units') is None:
            r['units'] = value
        out.append(r)
    return out


def _base(rows, request):
    out = _filled(rows, request.get('fill'))
    for r in out:
        region = r.get('region')
        r['region'] = region.strip().lower() if isinstance(region, str) else region
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    out = _filled(rows, request.get('fill'))
    for r in out:
        x = r.get('region')
        r['region'] = x.strip().lower() if isinstance(x, str) else x
    return out


def revenue(rows, lookup, request):
    return _base(rows, request)


def _aggregate(groups, agg):
    result = []
    for key, vals in groups.items():
        vals = [v for v in vals if v is not None]
        if agg == 'count': value = len(vals)
        elif agg == 'mean': value = sum(vals) / len(vals) if vals else None
        else: value = sum(vals)
        result.append((key, value))
    return result


def group(rows, lookup, request):
    groups = defaultdict(list)
    for r in _base(rows, request):
        key = r.get('region')
        if key is not None: groups[key].append(r['revenue_cents'])
    pairs = _aggregate(groups, request.get('agg'))
    pairs.sort(key=lambda x: str(x[0]))
    field = request.get('agg') + '_revenue_cents'
    return [{'region': k, field: v} for k, v in pairs]


def monthly(rows, lookup, request):
    groups = defaultdict(list)
    for r in _base(rows, request):
        date, region = r.get('date'), r.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups[(month, region)].append(r['revenue_cents'])
    pairs = _aggregate(groups, request.get('agg'))
    pairs.sort(key=lambda x: (str(x[0][0]), str(x[0][1])))
    field = request.get('agg') + '_revenue_cents'
    return [{'month': k[0], 'region': k[1], field: v} for k, v in pairs]


def lookup(rows, lookup, request):
    out = _base(rows, request)
    targets = {x.get('region'): x.get('target') for x in lookup}
    for r in out:
        target, revenue = targets.get(r.get('region')), r['revenue_cents']
        r['revenue_cents_per_target'] = None if target in (None, 0) or revenue is None else revenue / target
    return out


def window(rows, lookup, request):
    out = _base(rows, request)
    width = request.get('window')
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
