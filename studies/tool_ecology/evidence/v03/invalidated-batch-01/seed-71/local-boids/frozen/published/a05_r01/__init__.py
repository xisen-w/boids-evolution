"""Reusable row-oriented implementations of six table service families."""
from statistics import median


def _base(rows, request):
    fill = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = {'zero': 0, 'mean': (sum(vals) / len(vals) if vals else 0),
                   'median': (median(vals) if vals else 0)}.get(fill)
    if fill not in ('zero', 'mean', 'median'):
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out = []
    for row in rows:
        d = dict(row)
        if d.get('units') is None:
            d['units'] = replacement
        if 'region' in d:
            d['region'] = d['region'].strip().lower() if d['region'] is not None else None
        out.append(d)
    return out


def _revenue(rows, request):
    out = _base(rows, request)
    for d in out:
        u, p = d.get('units'), d.get('price_cents')
        d['revenue_cents'] = None if u is None or p is None else u * p
    return out


def clean(rows, lookup, request):
    return _base(rows, request)


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def group(rows, lookup, request):
    agg = request.get('agg', 'sum')
    if agg not in ('sum', 'mean', 'count'):
        raise ValueError("agg must be 'sum', 'mean', or 'count'")
    groups = {}
    for d in _revenue(rows, request):
        key, value = d.get('region'), d['revenue_cents']
        if key is not None:
            groups.setdefault(key, []).append(value)
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(v, agg)}
            for k, v in sorted(groups.items(), key=lambda item: str(item[0]))]


def _aggregate(values, agg):
    nums = [x for x in values if x is not None]
    if agg == 'count': return len(nums)
    if agg == 'sum': return sum(nums) if nums else 0
    return sum(nums) / len(nums) if nums else None


def monthly(rows, lookup, request):
    agg = request.get('agg', 'sum')
    if agg not in ('sum', 'mean', 'count'):
        raise ValueError("agg must be 'sum', 'mean', or 'count'")
    groups = {}
    for d in _revenue(rows, request):
        date, region = d.get('date'), d.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(d['revenue_cents'])
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(v, agg)}
            for (m, r), v in sorted(groups.items(), key=lambda item: (str(item[0][0]), str(item[0][1])))]


def lookup(rows, lookup, request):
    out = _revenue(rows, request)
    targets = {item.get('region'): item.get('target') for item in lookup}
    for d in out:
        region, value = d.get('region'), d['revenue_cents']
        target = targets.get(region)
        d['revenue_cents_per_target'] = (None if region not in targets or target in (None, 0) or value is None
                                         else value / target)
    return out


def window(rows, lookup, request):
    out = _revenue(rows, request)
    width = request.get('window', 2)
    if width not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    for i, d in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-width+1):i+1]
                if x['revenue_cents'] is not None]
        d['roll_revenue_cents'] = sum(vals) / len(vals) if vals else None
    return out
