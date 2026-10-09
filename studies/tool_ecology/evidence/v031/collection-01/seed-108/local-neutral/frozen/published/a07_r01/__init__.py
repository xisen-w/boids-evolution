"""Native table transformations for the six recurring table service families."""
from statistics import median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _prepared(rows, request):
    """Copy rows, normalize regions, fill units, and derive revenue."""
    fill = request.get('fill', 'zero')
    values = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero' or not values:
        replacement = 0
    elif fill == 'mean':
        replacement = sum(values) / len(values)
    elif fill == 'median':
        replacement = median(values)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    result = []
    for source in rows:
        row = dict(source)
        row['region'] = _region(row.get('region'))
        if row.get('units') is None:
            row['units'] = replacement
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
        result.append(row)
    return result


def clean(rows, lookup, request):
    """Normalize region and fill missing units; preserve all other columns."""
    fill = request.get('fill', 'zero')
    values = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero' or not values: replacement = 0
    elif fill == 'mean': replacement = sum(values) / len(values)
    elif fill == 'median': replacement = median(values)
    else: raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out=[]
    for source in rows:
        row=dict(source); row['region']=_region(row.get('region'))
        if row.get('units') is None: row['units']=replacement
        out.append(row)
    return out


def revenue(rows, lookup, request):
    """Fill units and append revenue_cents to every row."""
    return _prepared(rows, request)


def _aggregate(values, agg):
    vals=[v for v in values if v is not None]
    if agg == 'sum': return sum(vals)
    if agg == 'count': return len(vals)
    if agg == 'mean': return sum(vals)/len(vals) if vals else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    """Return normalized-region aggregate rows, dropping missing regions."""
    agg=request.get('agg','sum'); data={}
    for row in _prepared(rows, request):
        key=row.get('region')
        if key is not None: data.setdefault(key, []).append(row['revenue_cents'])
    name=agg+'_revenue_cents'
    return [{'region': key, name: _aggregate(data[key], agg)} for key in sorted(data, key=str)]


def monthly(rows, lookup, request):
    """Return aggregates grouped by ISO month and normalized region."""
    agg=request.get('agg','sum'); data={}
    for row in _prepared(rows, request):
        date=row.get('date'); region=row.get('region')
        month=date[:7] if date is not None else None
        if month is not None and region is not None:
            data.setdefault((month,region), []).append(row['revenue_cents'])
    name=agg+'_revenue_cents'
    keys=sorted(data, key=lambda k:(str(k[0]),str(k[1])))
    return [{'month':m,'region':r,name:_aggregate(data[(m,r)],agg)} for m,r in keys]


def lookup(rows, lookup, request):
    """Append revenue_cents_per_target using exact normalized region lookup."""
    targets={_region(item.get('region')): item.get('target') for item in lookup}
    out=[]
    for row in _prepared(rows, request):
        target=targets.get(row.get('region'))
        rev=row['revenue_cents']
        row['revenue_cents_per_target'] = None if target is None or target == 0 or rev is None else rev/target
        out.append(row)
    return out


def window(rows, lookup, request):
    """Append trailing-row mean revenue, including current row."""
    data=_prepared(rows, request); width=request.get('window')
    if width not in (2,3,4): raise ValueError('window must be 2, 3, or 4')
    out=[]; prior=[]
    for row in data:
        prior.append(row['revenue_cents'])
        vals=[v for v in prior[-width:] if v is not None]
        row['roll_revenue_cents']=sum(vals)/len(vals) if vals else None
        out.append(row)
    return out
