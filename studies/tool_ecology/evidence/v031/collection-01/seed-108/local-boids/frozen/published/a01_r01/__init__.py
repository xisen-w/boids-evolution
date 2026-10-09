"""Native implementations of the recurring tabular service families."""
from statistics import mean, median


def _fill(rows, method):
    vals = [r.get('units') for r in rows if r.get('units') is not None]
    replacement = 0 if not vals else (mean(vals) if method == 'mean' else median(vals) if method == 'median' else 0)
    out=[]
    for row in rows:
        x=dict(row)
        if x.get('units') is None: x['units']=replacement
        out.append(x)
    return out


def _base(rows, request):
    out=_fill(rows, request.get('fill', 'zero'))
    for x in out:
        reg=x.get('region')
        x['region']=reg.strip().lower() if isinstance(reg,str) else None
        u,p=x.get('units'),x.get('price_cents')
        x['revenue_cents']=None if u is None or p is None else u*p
    return out


def clean(rows, lookup, request):
    out=_fill(rows, request.get('fill','zero'))
    for x in out:
        r=x.get('region'); x['region']=r.strip().lower() if isinstance(r,str) else None
    return out


def revenue(rows, lookup, request):
    return _base(rows,request)


def _aggregate(rows, agg):
    vals=[x['revenue_cents'] for x in rows if x['revenue_cents'] is not None]
    if agg=='count': return len(vals)
    if agg=='mean': return sum(vals)/len(vals) if vals else None
    return sum(vals) if vals else 0


def group(rows, lookup, request):
    buckets={}
    for x in _base(rows,request):
        k=x.get('region')
        if k is not None: buckets.setdefault(k,[]).append(x)
    agg=request.get('agg','sum')
    return [{'region':k, f'{agg}_revenue_cents':_aggregate(v,agg)} for k,v in sorted(buckets.items(), key=lambda z:str(z[0]))]


def monthly(rows, lookup, request):
    buckets={}
    for x in _base(rows,request):
        date=x.get('date'); month=date[:7] if date is not None else None
        x['month']=month
        if month is not None and x.get('region') is not None:
            buckets.setdefault((month,x['region']),[]).append(x)
    agg=request.get('agg','sum')
    return [{'month':m,'region':r,f'{agg}_revenue_cents':_aggregate(v,agg)} for (m,r),v in sorted(buckets.items(),key=lambda z:(str(z[0][0]),str(z[0][1])))]


def lookup(rows, lookup, request):
    out=_base(rows,request)
    targets={}
    for x in lookup:
        r=x.get('region'); key=r.strip().lower() if isinstance(r,str) else r
        targets[key]=x.get('target')
    for x in out:
        target=targets.get(x.get('region')); rev=x['revenue_cents']
        x['revenue_cents_per_target']=None if target is None or target==0 or rev is None else rev/target
    return out


def window(rows, lookup, request):
    out=_base(rows,request)
    n=request.get('window',2)
    if not isinstance(n,int) or n<1: raise ValueError('window must be a positive integer')
    for i,x in enumerate(out):
        vals=[y['revenue_cents'] for y in out[max(0,i-n+1):i+1] if y['revenue_cents'] is not None]
        x['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return out
