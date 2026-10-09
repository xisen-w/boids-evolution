"""Native implementations of tabular data service families."""
from statistics import mean, median


def _region(value):
    return value.strip().lower() if isinstance(value, str) else value


def _filled_rows(rows, request):
    """Copy rows and apply request.fill to missing units."""
    fill = request.get('fill', 'zero')
    present = [r.get('units') for r in rows if r.get('units') is not None]
    if fill == 'zero' or not present:
        replacement = 0
    elif fill == 'mean':
        replacement = mean(present)
    elif fill == 'median':
        replacement = median(present)
    else:
        raise ValueError("fill must be 'zero', 'mean', or 'median'")
    out = []
    for row in rows:
        copied = dict(row)
        if copied.get('units') is None:
            copied['units'] = replacement
        out.append(copied)
    return out


def clean(rows, lookup, request):
    """Normalize region and fill units, retaining every row and column."""
    out = _filled_rows(rows, request)
    for row in out:
        if 'region' in row:
            row['region'] = _region(row['region'])
    return out


def _revenue_rows(rows, request, normalize_region=True):
    out = _filled_rows(rows, request)
    for row in out:
        if normalize_region:
            row['region'] = _region(row.get('region'))
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
    return out


def revenue(rows, lookup, request):
    """Normalize region, fill units, and append revenue_cents."""
    return _revenue_rows(rows, request, normalize_region=False)


def _aggregate(values, agg):
    nonmissing = [v for v in values if v is not None]
    if agg == 'sum':
        return sum(nonmissing)
    if agg == 'count':
        return len(nonmissing)
    if agg == 'mean':
        return mean(nonmissing) if nonmissing else None
    raise ValueError("agg must be 'sum', 'mean', or 'count'")


def group(rows, lookup, request):
    """Return per-region aggregate revenue rows."""
    agg = request.get('agg', 'sum')
    groups = {}
    for row in _revenue_rows(rows, request):
        key = row.get('region')
        if key is not None:
            groups.setdefault(key, []).append(row.get('revenue_cents'))
    return [{'region': key, f'{agg}_revenue_cents': _aggregate(groups[key], agg)}
            for key in sorted(groups, key=str)]


def monthly(rows, lookup, request):
    """Return aggregate revenue by month and normalized region."""
    agg = request.get('agg', 'sum')
    groups = {}
    for row in _revenue_rows(rows, request):
        date, region = row.get('date'), row.get('region')
        month = date[:7] if date is not None else None
        if month is not None and region is not None:
            groups.setdefault((month, region), []).append(row.get('revenue_cents'))
    keys = sorted(groups, key=lambda k: (str(k[0]), str(k[1])))
    return [{'month': m, 'region': r, f'{agg}_revenue_cents': _aggregate(groups[(m, r)], agg)}
            for m, r in keys]


def lookup_service(rows, lookup, request):
    """Append revenue_cents_per_target using normalized exact region keys."""
    targets = {}
    for item in lookup:
        targets[_region(item.get('region'))] = item.get('target')
    out = _revenue_rows(rows, request)
    for row in out:
        target = targets.get(row.get('region'))
        rev = row.get('revenue_cents')
        row['revenue_cents_per_target'] = (rev / target if rev is not None and target not in (None, 0) else None)
    return out


def window(rows, lookup, request):
    """Append trailing positional-window mean of nonmissing revenue."""
    size = request.get('window')
    if size not in (2, 3, 4):
        raise ValueError('window must be 2, 3, or 4')
    out = _revenue_rows(rows, request, normalize_region=False)
    for i, row in enumerate(out):
        values = [r['revenue_cents'] for r in out[max(0, i-size+1):i+1]
                  if r['revenue_cents'] is not None]
        row['roll_revenue_cents'] = mean(values) if values else None
    return out


# Root-level service adapters listed in publish.json.
def serve_clean(rows, lookup, request): return clean(rows, lookup, request)
def serve_revenue(rows, lookup, request): return revenue(rows, lookup, request)
def serve_group(rows, lookup, request): return group(rows, lookup, request)
def serve_monthly(rows, lookup, request): return monthly(rows, lookup, request)
def serve_lookup(rows, lookup, request): return lookup_service(rows, lookup, request)
def serve_window(rows, lookup, request): return window(rows, lookup, request)
