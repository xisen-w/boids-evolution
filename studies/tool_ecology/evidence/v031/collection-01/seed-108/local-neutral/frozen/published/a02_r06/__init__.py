"""Small dependency-free tabular service adapters."""
from statistics import mean, median

_MISSING = None

def _filled(rows, mode):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = {'zero': 0, 'mean': mean(vals) if vals else 0, 'median': median(vals) if vals else 0}.get(mode)
    if mode not in ('zero', 'mean', 'median'):
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out=[]
    for row in rows:
        d=dict(row)
        if d.get('units') is None: d['units']=replacement
        out.append(d)
    return out

def _normalized(rows):
    out=[]
    for row in rows:
        d=dict(row)
        if d.get('region') is not None: d['region']=d['region'].strip().lower()
        out.append(d)
    return out

def clean(rows, lookup, request):
    return _normalized(_filled(rows, request.get('fill', 'zero')))

def _revenue(rows, request):
    out=[]
    for d in _filled(rows, request.get('fill', 'zero')):
        d['revenue_cents'] = (d.get('units') * d.get('price_cents')) if d.get('units') is not None and d.get('price_cents') is not None else None
        out.append(d)
    return out

def revenue(rows, lookup, request):
    return _normalized(_revenue(rows, request))

def _aggregate(values, agg):
    valid=[v for v in values if v is not None]
    if agg == 'sum': return sum(valid)
    if agg == 'count': return len(valid)
    if agg == 'mean': return mean(valid) if valid else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")

def _groups(rows, request, monthly=False):
    records=revenue(rows, None, request)
    buckets={}
    for d in records:
        region=d.get('region')
        month=(d.get('date')[:7] if d.get('date') is not None else None) if monthly else None
        if region is None or (monthly and month is None): continue
        key=(month,region) if monthly else (region,)
        buckets.setdefault(key,[]).append(d.get('revenue_cents'))
    keys=sorted(buckets, key=lambda k: tuple(str(x) for x in k))
    agg=request.get('agg','sum')
    result=[]
    for key in keys:
        val=_aggregate(buckets[key],agg)
        if monthly: result.append({'month':key[0], 'region':key[1], agg+'_revenue_cents':val})
        else: result.append({'region':key[0], agg+'_revenue_cents':val})
    return result

def group(rows, lookup, request): return _groups(rows, request)
def monthly(rows, lookup, request): return _groups(rows, request, True)

def lookup_service(rows, lookup, request):
    targets={(d.get('region').strip().lower() if isinstance(d.get('region'), str) else d.get('region')):d.get('target') for d in lookup}
    out=[]
    for d in revenue(rows, None, request):
        target=targets.get(d.get('region'))
        d['revenue_cents_per_target'] = d.get('revenue_cents') / target if d.get('revenue_cents') is not None and target not in (None,0) else None
        out.append(d)
    return out

def window(rows, lookup, request):
    out=_revenue(rows,request)
    n=request.get('window', 2)
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,d in enumerate(out):
        vals=[x.get('revenue_cents') for x in out[max(0,i-n+1):i+1] if x.get('revenue_cents') is not None]
        d['roll_revenue_cents']=mean(vals) if vals else None
    return out

__all__=['clean','revenue','group','monthly','lookup_service','window']
