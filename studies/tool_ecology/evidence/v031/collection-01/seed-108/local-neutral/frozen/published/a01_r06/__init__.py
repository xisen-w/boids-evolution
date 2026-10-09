"""Native Python row-table service transformations."""
from statistics import mean, median

def _fill(rows, mode):
    vals=[r.get("units") for r in rows if r.get("units") is not None]
    value=0 if not vals else (0 if mode=="zero" else mean(vals) if mode=="mean" else median(vals))
    out=[]
    for row in rows:
        x=dict(row); x["region"] = row.get("region").strip().lower() if isinstance(row.get("region"), str) else row.get("region")
        if x.get("units") is None: x["units"]=value
        out.append(x)
    return out

def _rev(rows, req):
    out=_fill(rows,req.get("fill"))
    for r,src in zip(out, rows): r["revenue_cents"] = None if r.get("units") is None or src.get("price_cents") is None else r["units"]*src["price_cents"]
    return out

def clean_service(rows, lookup, request): return _fill(rows,request.get("fill"))
def revenue_service(rows, lookup, request): return _rev(rows,request)
def _aggregate(vals, agg):
    vals=[v for v in vals if v is not None]
    return sum(vals) if agg=="sum" else (len(vals) if agg=="count" else (sum(vals)/len(vals) if vals else None))
def group_service(rows,lookup,request):
    data=_rev(rows,request); groups={}
    for r in data:
        k=r.get("region")
        if k is not None: groups.setdefault(k,[]).append(r.get("revenue_cents"))
    agg=request.get("agg"); return [{"region":k,agg+"_revenue_cents":_aggregate(v,agg)} for k,v in sorted(groups.items(),key=lambda x:str(x[0]))]
def monthly_service(rows,lookup,request):
    groups={}
    for r in _rev(rows,request):
        date=r.get("date"); region=r.get("region")
        month=date[:7] if date is not None else None
        if month is not None and region is not None: groups.setdefault((month,region),[]).append(r.get("revenue_cents"))
    agg=request.get("agg"); return [{"month":k[0],"region":k[1],agg+"_revenue_cents":_aggregate(v,agg)} for k,v in sorted(groups.items(),key=lambda x:(str(x[0][0]),str(x[0][1])))]
def lookup_service(rows,lookup,request):
    data=_rev(rows,request); targets={r.get("region"):r.get("target") for r in lookup}
    for r in data:
        t=targets.get(r.get("region")); v=r.get("revenue_cents")
        r["revenue_cents_per_target"] = None if t is None or t==0 or v is None else v/t
    return data
def window_service(rows,lookup,request):
    data=_rev(rows,request); window=request.get("window"); history=[]
    for r in data:
        history.append(r.get("revenue_cents")); vals=[x for x in history[-window:] if x is not None]
        r["roll_revenue_cents"] = sum(vals)/len(vals) if vals else None
    return data
