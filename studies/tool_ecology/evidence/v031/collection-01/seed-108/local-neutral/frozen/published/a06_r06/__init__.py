"""Pure-Python transformations for sales-row service requests."""
from statistics import mean, median


def _norm(x):
    return x.strip().lower() if isinstance(x, str) else x


def _base(rows, request, normalize=True):
    vals = [r['units'] for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    fill = (mean(vals) if vals else 0) if mode == 'mean' else (median(vals) if vals else 0) if mode == 'median' else 0
    out = []
    for source in rows:
        row = dict(source)
        if normalize:
            row['region'] = _norm(row.get('region'))
        if row.get('units') is None:
            row['units'] = fill
        out.append(row)
    return out


def clean(rows, lookup, request):
    return _base(rows, request)


def revenue(rows, lookup, request):
    out = _base(rows, request, False)
    for r in out:
        u, p = r.get('units'), r.get('price_cents')
        r['revenue_cents'] = None if u is None or p is None else u * p
    return out


def _agg(vals, op):
    vals = [v for v in vals if v is not None]
    if op == 'count': return len(vals)
    if op == 'mean': return mean(vals) if vals else None
    return sum(vals)


def group(rows, lookup, request):
    groups = {}
    for r in revenue(rows, lookup, request):
        key = _norm(r.get('region'))
        if key is not None: groups.setdefault(key, []).append(r['revenue_cents'])
    op = request.get('agg', 'sum')
    return [{'region': k, op+'_revenue_cents': _agg(v, op)} for k,v in sorted(groups.items(), key=lambda x: str(x[0]))]


def monthly(rows, lookup, request):
    groups = {}
    for r in revenue(rows, lookup, request):
        region, date = _norm(r.get('region')), r.get('date')
        month = date[:7] if date is not None else None
        if region is not None and month is not None: groups.setdefault((month,region), []).append(r['revenue_cents'])
    op = request.get('agg', 'sum')
    return [{'month':m,'region':r,op+'_revenue_cents':_agg(groups[(m,r)],op)} for m,r in sorted(groups,key=lambda x:(str(x[0]),str(x[1])))]


def lookup_service(rows, lookup, request):
    targets = {_norm(x.get('region')): x.get('target') for x in lookup}
    out = revenue(rows, lookup, request)
    for r in out:
        r['region'] = _norm(r.get('region'))
        t = targets.get(r.get('region'))
        v = r['revenue_cents']
        r['revenue_cents_per_target'] = None if t is None or t == 0 or v is None else v/t
    return out


def window(rows, lookup, request):
    out = revenue(rows, lookup, request)
    size = request.get('window', 2)
    for i,r in enumerate(out):
        vals = [x['revenue_cents'] for x in out[max(0,i-size+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents'] = mean(vals) if vals else None
    return out

clean_service = clean
revenue_service = revenue
group_service = group
monthly_service = monthly
window_service = window
lookup = lookup_service
lookup_revenue = lookup_service
