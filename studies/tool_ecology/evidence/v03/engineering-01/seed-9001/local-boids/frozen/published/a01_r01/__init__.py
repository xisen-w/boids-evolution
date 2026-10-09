"""Native implementations of the recurring row-table services."""
from statistics import mean, median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _filled(rows, request):
    mode = request.get('fill', 'zero')
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    fill = {'zero': 0, 'mean': (mean(vals) if vals else 0), 'median': (median(vals) if vals else 0)}.get(mode)
    if mode not in ('zero', 'mean', 'median'):
        raise ValueError('fill must be zero, mean, or median')
    return [({**r, 'units': (fill if r.get('units') is None else r.get('units'))}) for r in rows]


def _revenue_rows(rows, request):
    out=[]
    for r in _filled(rows, request):
        rev = None if r.get('units') is None or r.get('price_cents') is None else r['units'] * r['price_cents']
        out.append({**r, 'revenue_cents': rev})
    return out


def clean(rows, lookup, request):
    return [{**r, 'region': _region(r.get('region'))} for r in _filled(rows, request)]


def revenue(rows, lookup, request):
    return [{**r, 'region': _region(r.get('region'))} for r in _revenue_rows(rows, request)]


def _aggregate(values, agg):
    valid=[v for v in values if v is not None]
    if agg == 'sum': return sum(valid)
    if agg == 'count': return len(valid)
    if agg == 'mean': return sum(valid)/len(valid) if valid else None
    raise ValueError('agg must be sum, mean, or count')


def group(rows, lookup, request):
    data=revenue(rows, lookup, request); groups={}
    for r in data:
        key=r.get('region')
        if key is not None: groups.setdefault(key, []).append(r.get('revenue_cents'))
    agg=request.get('agg', 'sum')
    return [{'region': k, f'{agg}_revenue_cents': _aggregate(groups[k], agg)} for k in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    data=revenue(rows, lookup, request); groups={}
    for r in data:
        date=r.get('date'); month=date[:7] if date is not None else None; region=r.get('region')
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(r.get('revenue_cents'))
    agg=request.get('agg', 'sum')
    return [{'month': m, 'region': reg, f'{agg}_revenue_cents': _aggregate(groups[(m,reg)], agg)}
            for m,reg in sorted(groups, key=lambda x: (str(x[0]), str(x[1])))]


def lookup(rows, lookup, request):
    data=revenue(rows, lookup, request)
    targets={_region(x.get('region')): x.get('target') for x in lookup if x.get('region') is not None}
    out=[]
    for r in data:
        target=targets.get(r.get('region')); rev=r.get('revenue_cents')
        value=None if target in (None, 0) or rev is None else rev/target
        out.append({**r, 'revenue_cents_per_target': value})
    return out


def window(rows, lookup, request):
    data=revenue(rows, lookup, request); width=request.get('window', 2)
    if not isinstance(width, int) or width <= 0: raise ValueError('window must be a positive integer')
    out=[]
    for i,r in enumerate(data):
        vals=[x.get('revenue_cents') for x in data[max(0,i-width+1):i+1] if x.get('revenue_cents') is not None]
        out.append({**r, 'roll_revenue_cents': sum(vals)/len(vals) if vals else None})
    return out
