"""Native implementations of the tabular service families."""
from statistics import mean, median

_MISSING = object()

def _region(value):
    return value.strip().lower() if isinstance(value, str) else value

def _filled_units(rows, request):
    vals = [r.get('units') for r in rows]
    present = [v for v in vals if v is not None]
    mode = request.get('fill', 'zero')
    if mode == 'zero' or not present:
        replacement = 0
    elif mode == 'mean':
        replacement = mean(present)
    elif mode == 'median':
        replacement = median(present)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [replacement if v is None else v for v in vals]

def clean(rows, lookup, request):
    units = _filled_units(rows, request)
    out=[]
    for row, units_value in zip(rows, units):
        item=dict(row); item['region']=_region(row.get('region')); item['units']=units_value; out.append(item)
    return out

def revenue(rows, lookup, request):
    base=clean(rows, lookup, request); out=[]
    for item in base:
        item['revenue_cents'] = None if item.get('units') is None or item.get('price_cents') is None else item['units'] * item['price_cents']
        out.append(item)
    return out

def _aggregate(values, agg):
    valid=[v for v in values if v is not None]
    if agg == 'sum': return sum(valid)
    if agg == 'count': return len(valid)
    if agg == 'mean': return sum(valid)/len(valid) if valid else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")

def group(rows, lookup, request):
    grouped={}
    for row in revenue(rows, lookup, request):
        key=row.get('region')
        if key is not None: grouped.setdefault(key, []).append(row.get('revenue_cents'))
    agg=request.get('agg', 'sum'); col=agg+'_revenue_cents'
    return [{'region':k, col:_aggregate(grouped[k],agg)} for k in sorted(grouped,key=str)]

def monthly(rows, lookup, request):
    grouped={}
    for row in revenue(rows, lookup, request):
        date=row.get('date'); region=row.get('region')
        month=date[:7] if date is not None else None
        if month is not None and region is not None:
            grouped.setdefault((month,region),[]).append(row.get('revenue_cents'))
    agg=request.get('agg','sum'); col=agg+'_revenue_cents'
    keys=sorted(grouped,key=lambda k:(str(k[0]),str(k[1])))
    return [{'month':m,'region':r,col:_aggregate(grouped[(m,r)],agg)} for m,r in keys]

def lookup(rows, lookup, request):
    targets={_region(entry.get('region')):entry.get('target') for entry in lookup}
    out=[]
    for item in revenue(rows,lookup,request):
        target=targets.get(item.get('region')); value=item.get('revenue_cents')
        item['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value/target
        out.append(item)
    return out

def window(rows, lookup, request):
    base=revenue(rows,lookup,request); width=request.get('window',2)
    if width not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    out=[]
    for i,item in enumerate(base):
        vals=[r.get('revenue_cents') for r in base[max(0,i-width+1):i+1] if r.get('revenue_cents') is not None]
        item['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
        out.append(item)
    return out

# Explicit service adapter names for publication.
serve_clean=clean
serve_revenue=revenue
serve_group=group
serve_monthly=monthly
serve_lookup=lookup
serve_window=window
