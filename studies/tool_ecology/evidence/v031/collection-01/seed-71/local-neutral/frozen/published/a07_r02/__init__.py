"""Native implementations of the tabular service families."""
from statistics import mean, median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _fill_units(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero':
        replacement = 0
    elif mode == 'mean':
        replacement = mean(vals) if vals else 0
    elif mode == 'median':
        replacement = median(vals) if vals else 0
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [dict(r, units=(replacement if r.get('units') is None else r.get('units'))) for r in rows]


def clean(rows, lookup, request):
    """Normalize region and fill missing units; preserve every other field/order."""
    return [dict(r, region=_region(r.get('region'))) for r in _fill_units(rows, request['fill'])]


def _revenue_rows(rows, fill):
    output = []
    for r in _fill_units(rows, fill):
        d = dict(r)
        u, p = d.get('units'), d.get('price_cents')
        d['revenue_cents'] = None if u is None or p is None else u * p
        output.append(d)
    return output


def revenue(rows, lookup, request):
    """Fill units and append revenue_cents, retaining original column order."""
    return _revenue_rows(rows, request['fill'])


def _grouped(rows, request, monthly=False):
    data = _revenue_rows(rows, request['fill'])
    groups = {}
    for r in data:
        region = _region(r.get('region'))
        if monthly:
            date = r.get('date')
            month = date[:7] if date is not None else None
            if month is None or region is None:
                continue
            key = (month, region)
        else:
            if region is None:
                continue
            key = (region,)
        groups.setdefault(key, []).append(r['revenue_cents'])
    agg = request['agg']
    if agg not in ('sum', 'mean', 'count'):
        raise ValueError("agg must be 'sum', 'mean', or 'count'")
    result = []
    for key, values in groups.items():
        valid = [v for v in values if v is not None]
        if agg == 'sum':
            value = sum(valid)
        elif agg == 'count':
            value = len(valid)
        else:
            value = mean(valid) if valid else None
        if monthly:
            result.append({'month': key[0], 'region': key[1], agg + '_revenue_cents': value})
        else:
            result.append({'region': key[0], agg + '_revenue_cents': value})
    result.sort(key=lambda r: tuple(str(r[k]) for k in (('month', 'region') if monthly else ('region',))))
    return result


def group(rows, lookup, request):
    """Group by normalized region and aggregate nonmissing revenue."""
    return _grouped(rows, request)


def monthly(rows, lookup, request):
    """Group by YYYY-MM and normalized region."""
    return _grouped(rows, request, monthly=True)


def lookup(rows, lookup, request):
    """Append revenue and revenue_cents_per_target using exact normalized region keys."""
    targets = {_region(x.get('region')): x.get('target') for x in lookup}
    result = []
    for r in _revenue_rows(rows, request['fill']):
        d = dict(r)
        region = _region(d.get('region'))
        d['region'] = region
        target = targets.get(region)
        rev = d['revenue_cents']
        d['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev / target
        result.append(d)
    return result


def window(rows, lookup, request):
    """Append trailing ROWS-window mean of nonmissing revenue."""
    n = request['window']
    if n not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    data = _revenue_rows(rows, request['fill'])
    out = []
    revenues = []
    for d in data:
        revenues.append(d['revenue_cents'])
        values = [v for v in revenues[-n:] if v is not None]
        x = dict(d)
        x['roll_revenue_cents'] = mean(values) if values else None
        out.append(x)
    return out


__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
