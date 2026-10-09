from statistics import mean, median

def _filled(rows, request):
    vals=[r.get('units') for r in rows if r.get('units') is not None]
    mode=request.get('fill','zero')
    x=0 if not vals or mode=='zero' else mean(vals) if mode=='mean' else median(vals) if mode=='median' else 0
    return [dict(r, **({'units':x} if r.get('units') is None else {})) for r in rows]

def _normalize(rows):
    out=[]
    for r in rows:
        q=dict(r)
        if q.get('region') is not None: q['region']=q['region'].strip().lower()
        out.append(q)
    return out

def clean_service(rows,lookup,request): return _normalize(_filled(rows,request))
def _revenue(rows,request):
    out=_filled(rows,request)
    for r in out:
        u,p=r.get('units'),r.get('price_cents')
        r['revenue_cents']=None if u is None or p is None else u*p
    return out
def revenue_service(rows,lookup,request): return _revenue(rows,request)
def _aggregate(vals,agg):
    v=[x for x in vals if x is not None]
    return len(v) if agg=='count' else (sum(v)/len(v) if v else None) if agg=='mean' else sum(v) if v else 0
def _group(rows,request,monthly=False):
    agg=request.get('agg','sum'); data=_normalize(_revenue(rows,request)); groups={}
    for r in data:
        region=r.get('region'); date=r.get('date')
        if region is None or (monthly and date is None): continue
        key=(date[:7],region) if monthly else (region,)
        groups.setdefault(key,[]).append(r['revenue_cents'])
    keys=['month','region'] if monthly else ['region']; out=[]
    for k,vals in groups.items(): out.append(dict(zip(keys,k), **{agg+'_revenue_cents':_aggregate(vals,agg)}))
    out.sort(key=lambda r:tuple(str(r[k]) for k in keys)); return out
def group_service(rows,lookup,request): return _group(rows,request)
def monthly_service(rows,lookup,request): return _group(rows,request,True)
def lookup_service(rows,lookup,request):
    data=_normalize(_revenue(rows,request)); targets={}
    for x in lookup:
        if x.get('region') is not None: targets[x['region'].strip().lower()]=x.get('target')
    for r in data:
        t=targets.get(r.get('region')); v=r['revenue_cents']
        r['revenue_cents_per_target']=None if t is None or t==0 or v is None else v/t
    return data
def window_service(rows,lookup,request):
    data=_revenue(rows,request); n=request.get('window',2)
    for i,r in enumerate(data):
        vals=[x['revenue_cents'] for x in data[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
    return data
