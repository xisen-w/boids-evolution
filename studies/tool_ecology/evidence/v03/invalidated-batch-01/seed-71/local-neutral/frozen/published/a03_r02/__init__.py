"""Pure Python row-table analytics."""
from statistics import median


def _fill(rows, mode):
    if mode not in ('zero', 'mean', 'median'):
        raise ValueError('fill must be zero, mean, or median')
    values = [r.get('units') for r in rows if r.get('units') is not None]
    if not values:
        return 0
    if mode == 'zero':
        return 0
    return sum(values) / len(values) if mode == 'mean' else median(values)


def _prep(rows, request):
    fill = _fill(rows, request.get('fill', 'zero'))
    out = []
    for row in rows:
        r = dict(row)
        if r.get('region') is not None:
            r['region'] = r['region'].strip().lower()
        if r.get('units') is None:
            r['units'] = fill
        out.append(r)
    return out


def clean(rows, lookup, request):
    return _prep(rows, request)


def _revenue(rows, request):
    out = _prep(rows, request)
    for r in out:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _agg(values, kind):
    vals = [v for v in values if v is not None]
    if kind == 'sum': return sum(vals)
    if kind == 'count': return len(vals)
    if kind == 'mean': return sum(vals) / len(vals) if vals else None
    raise ValueError('agg must be sum, mean, or count')


def _groups(rows, request, monthly_mode):
    kind = request.get('agg', 'sum')
    if kind not in ('sum', 'mean', 'count'): raise ValueError('invalid agg')
    groups = {}
    for r in _revenue(rows, request):
        region = r.get('region')
        month = r.get('date')
        month = None if month is None else month[:7]
        if region is None or (monthly_mode and month is None): continue
        key = (month, region) if monthly_mode else (region,)
        groups.setdefault(key, []).append(r['revenue_cents'])
    result = []
    for key in sorted(groups, key=lambda x: tuple(str(v) for v in x)):
        val = _agg(groups[key], kind)
        if monthly_mode:
            result.append({'month': key[0], 'region': key[1], kind+'_revenue_cents': val})
        else:
            result.append({'region': key[0], kind+'_revenue_cents': val})
    return result


def group(rows, lookup, request):
    return _groups(rows, request, False)


def monthly(rows, lookup, request):
    return _groups(rows, request, True)


def lookup(rows, lookup, request):
    out = _revenue(rows, request)
    targets = {}
    for item in lookup:
        key = item.get('region')
        if key is not None: targets[key.strip().lower()] = item.get('target')
    for r in out:
        target = targets.get(r.get('region'))
        value = r['revenue_cents']
        r['revenue_cents_per_target'] = None if value is None or target is None or target == 0 else value / target
    return out


def window(rows, lookup, request):
    n = request.get('window', 2)
    if n not in (2, 3, 4): raise ValueError('window must be 2, 3, or 4')
    out = _revenue(rows, request)
    for i, r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0, i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = sum(vals)/len(vals) if vals else None
    return out
