from statistics import mean, median

def _norm(v): return v.strip().lower() if isinstance(v,str) else v

def _filled(rows, fill, normalize=False):
    vals=[r.get('units') for r in rows if r.get('units') is not None]
    replacement={'zero':0,'mean':mean(vals) if vals else 0,'median':median(vals) if vals else 0}[fill]
    out=[]
    for r in rows:
        x=dict(r)
        if normalize: x['region']=_norm(x.get('region'))
        if x.get('units') is None: x['units']=replacement
        out.append(x)
    return out

def _revenue(rows, request, normalize=False):
    out=_filled(rows,request['fill'],normalize)
    for r in out:
        u,p=r.get('units'),r.get('price_cents')
        r['revenue_cents']=None if u is None or p is None else u*p
    return out

def clean(rows,lookup,request): return _filled(rows,request['fill'],True)
def revenue(rows,lookup,request): return _revenue(rows,request)
def group(rows,lookup,request): return _group(rows,request,False)
def monthly(rows,lookup,request): return _group(rows,request,True)
def _group(rows,request,monthly):
    data=_revenue(rows,request,True); groups={}
    for r in data:
        reg=r.get('region'); date=r.get('date'); month=date[:7] if monthly and date is not None else None
        if reg is None or (monthly and month is None): continue
        key=(month,reg) if monthly else (reg,)
        groups.setdefault(key,[]).append(r.get('revenue_cents'))
    agg=request['agg']; result=[]
    for k,vs in groups.items():
        vs=[v for v in vs if v is not None]
        val=len(vs) if agg=='count' else sum(vs) if agg=='sum' else mean(vs) if vs else None
        result.append((k,val))
    result.sort(key=lambda z:tuple(str(x) for x in z[0]))
    if monthly:return [{'month':k[0],'region':k[1],agg+'_revenue_cents':v} for k,v in result]
    return [{'region':k[0],agg+'_revenue_cents':v} for k,v in result]
def lookup(rows,lookup,request):
    data=_revenue(rows,request,True); targets={_norm(x.get('region')):x.get('target') for x in lookup}
    for r in data:
        t=targets.get(r.get('region')); v=r['revenue_cents']
        r['revenue_cents_per_target']=None if t is None or t==0 or v is None else v/t
    return data
def window(rows,lookup,request):
    data=_revenue(rows,request); n=request['window']
    for i,r in enumerate(data):
        vals=[x['revenue_cents'] for x in data[max(0,i-n+1):i+1] if x['revenue_cents'] is not None]
        r['roll_revenue_cents']=mean(vals) if vals else None
    return data
