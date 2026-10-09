"""Small, dependency-free implementations of the tabular service families."""
from statistics import mean, median


def _filled(rows, request):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero': value = 0
    elif mode == 'mean': value = mean(vals) if vals else 0
    elif mode == 'median': value = median(vals) if vals else 0
    else: raise ValueError("fill must be zero, mean, or median")
    out=[]
    for row in rows:
        x=dict(row)
        if x.get('units') is None: x['units']=value
        out.append(x)
    return out


def _norm(rows):
    out=[]
    for r in rows:
        x=dict(r)
        if x.get('region') is not None: x['region']=x['region'].strip().lower()
        out.append(x)
    return out


def _revenue(rows, request):
    out=[]
    for x in _filled(rows, request):
        p=x.get('price_cents'); u=x.get('units')
        x['revenue_cents'] = None if u is None or p is None else u*p
        out.append(x)
    return out


def clean(rows, lookup, request):
    return _filled(_norm(rows), request)


def revenue(rows, lookup, request):
    return _revenue(rows, request)


def _agg(values, agg):
    vals=[v for v in values if v is not None]
    if agg=='sum': return sum(vals)
    if agg=='count': return len(vals)
    if agg=='mean': return sum(vals)/len(vals) if vals else None
    raise ValueError('agg must be sum, mean, or count')


def group(rows, lookup, request):
    buckets={}
    for x in _revenue(_norm(rows), request):
        key=x.get('region')
        if key is not None: buckets.setdefault(key, []).append(x['revenue_cents'])
    agg=request.get('agg','sum')
    return [{'region':k, agg+'_revenue_cents':_agg(buckets[k],agg)} for k in sorted(buckets,key=str)]


def monthly(rows, lookup, request):
    buckets={}
    for x in _revenue(_norm(rows), request):
        date=x.get('date'); region=x.get('region')
        month=date[:7] if date is not None else None
        if month is not None and region is not None: buckets.setdefault((month,region), []).append(x['revenue_cents'])
    agg=request.get('agg','sum')
    return [{'month':m,'region':r,agg+'_revenue_cents':_agg(buckets[(m,r)],agg)} for m,r in sorted(buckets,key=lambda k:(str(k[0]),str(k[1])))]


def lookup(rows, lookup, request):
    targets={x.get('region'):x.get('target') for x in lookup}
    out=[]
    for x in _revenue(_norm(rows),request):
        target=targets.get(x.get('region')); val=x['revenue_cents']
        x['revenue_cents_per_target']=None if target is None or target==0 or val is None else val/target
        out.append(x)
    return out


def window(rows, lookup, request):
    n=request.get('window')
    if n not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    out=[]; revenues=[]
    for x in _revenue(rows,request):
        revenues.append(x['revenue_cents'])
        vals=[v for v in revenues[-n:] if v is not None]
        x['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
        out.append(x)
    return out
