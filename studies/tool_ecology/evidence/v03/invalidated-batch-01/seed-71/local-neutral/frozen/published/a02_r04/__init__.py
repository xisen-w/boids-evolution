"""Pure-Python tabular service adapters."""
from statistics import mean, median


def _units(rows, fill):
    vals = [r.get('units') for r in rows]
    present = [v for v in vals if v is not None]
    replacement = {'zero': 0, 'mean': lambda: mean(present) if present else 0,
                   'median': lambda: median(present) if present else 0}[fill]
    if callable(replacement):
        replacement = replacement()
    return [replacement if v is None else v for v in vals]


def _prepare(rows, request):
    units = _units(rows, request['fill'])
    out = []
    for row, unit in zip(rows, units):
        x = row.copy()
        x['region'] = row.get('region').strip().lower() if row.get('region') is not None else None
        x['units'] = unit
        price = row.get('price_cents')
        x['revenue_cents'] = unit * price if unit is not None and price is not None else None
        out.append(x)
    return out


def clean(rows, lookup, request):
    units = _units(rows, request['fill'])
    result=[]
    for r, u in zip(rows, units):
        x=r.copy(); x['region']=r.get('region').strip().lower() if r.get('region') is not None else None; x['units']=u; result.append(x)
    return result


def revenue(rows, lookup, request):
    return _prepare(rows, request)


def _aggregate(values, agg):
    vals=[v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    return mean(vals) if vals else None


def _group(rows, request, monthly):
    prepared=_prepare(rows, request); groups={}
    for r in prepared:
        key=((r.get('date')[:7] if r.get('date') is not None else None), r.get('region')) if monthly else (r.get('region'),)
        if any(v is None for v in key): continue
        groups.setdefault(key, []).append(r['revenue_cents'])
    agg=request['agg']; col=agg+'_revenue_cents'; result=[]
    for key in sorted(groups, key=lambda k: tuple(str(x) for x in k)):
        values=groups[key]
        item=({'month':key[0], 'region':key[1]} if monthly else {'region':key[0]})
        item[col]=_aggregate(values, agg); result.append(item)
    return result


def group(rows, lookup, request): return _group(rows, request, False)
def monthly(rows, lookup, request): return _group(rows, request, True)


def lookup_service(rows, lookup, request):
    prepared=_prepare(rows, request)
    targets={r.get('region'):r.get('target') for r in lookup}
    for r in prepared:
        target=targets.get(r.get('region')); rev=r['revenue_cents']
        r['revenue_cents_per_target']=rev/target if target not in (None, 0) and rev is not None else None
    return prepared


def window(rows, lookup, request):
    prepared=_prepare(rows, request); n=request['window']; history=[]
    for r in prepared:
        history.append(r['revenue_cents']); vals=[v for v in history[-n:] if v is not None]
        r['roll_revenue_cents']=mean(vals) if vals else None
    return prepared
