"""Small, dependency-free table transformations for sales-like row dictionaries."""
from statistics import mean, median


def _filled(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    if method == 'zero': value = 0
    elif method == 'mean': value = mean(vals) if vals else 0
    elif method == 'median': value = median(vals) if vals else 0
    else: raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out=[]
    for r in rows:
        x=dict(r)
        if x.get('units') is None: x['units']=value
        out.append(x)
    return out


def _normalize(rows):
    out=[]
    for r in rows:
        x=dict(r)
        if x.get('region') is not None: x['region']=x['region'].strip().lower()
        out.append(x)
    return out


def _revenue(rows, req):
    out=_filled(rows, req.get('fill'))
    for r in out:
        u=r.get('units'); p=r.get('price_cents')
        r['revenue_cents']=None if u is None or p is None else u*p
    return out


def clean(rows, lookup, request):
    return _normalize(_filled(rows, request.get('fill')))


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _aggregate(values, agg):
    vals=[v for v in values if v is not None]
    if agg=='sum': return sum(vals)
    if agg=='count': return len(vals)
    if agg=='mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("agg must be sum, mean, or count")


def group(rows, lookup, request):
    grouped={}
    for r in _normalize(_revenue(rows, request)):
        key=r.get('region')
        if key is not None: grouped.setdefault(key,[]).append(r.get('revenue_cents'))
    agg=request.get('agg')
    return [{'region':k, agg+'_revenue_cents':_aggregate(grouped[k],agg)} for k in sorted(grouped,key=str)]


def monthly(rows, lookup, request):
    grouped={}
    for r in _normalize(_revenue(rows, request)):
        date=r.get('date'); month=date[:7] if date is not None else None; region=r.get('region')
        if month is not None and region is not None: grouped.setdefault((month,region),[]).append(r.get('revenue_cents'))
    agg=request.get('agg')
    return [{'month':m,'region':r,agg+'_revenue_cents':_aggregate(grouped[(m,r)],agg)} for m,r in sorted(grouped,key=lambda x:(str(x[0]),str(x[1])))]


def lookup_service(rows, lookup, request):
    out=_normalize(_revenue(rows,request))
    targets={r.get('region'):r.get('target') for r in lookup}
    for r in out:
        region=r.get('region'); target=targets.get(region); rev=r.get('revenue_cents')
        r['revenue_cents_per_target']=None if target is None or target==0 or rev is None else rev/target
    return out


def window(rows, lookup, request):
    out=_revenue(rows,request); n=request.get('window')
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    for i,r in enumerate(out):
        vals=[x.get('revenue_cents') for x in out[max(0,i-n+1):i+1] if x.get('revenue_cents') is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out
