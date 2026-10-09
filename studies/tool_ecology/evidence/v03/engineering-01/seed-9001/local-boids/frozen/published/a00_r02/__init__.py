"""Revenue and trailing-row services with nonmutating row handling."""
from statistics import mean, median


def _filled(rows, request):
    mode = request.get('fill', 'zero')
    present = [r.get('units') for r in rows if r.get('units') is not None]
    if mode == 'zero': value = 0
    elif mode == 'mean': value = mean(present) if present else 0
    elif mode == 'median': value = median(present) if present else 0
    else: raise ValueError("fill must be 'zero', 'mean', or 'median'")
    return [value if r.get('units') is None else r.get('units') for r in rows]


def revenue(rows, lookup, request):
    """Return copied rows with units filled and revenue_cents derived."""
    result = []
    for row, units in zip(rows, _filled(rows, request)):
        out = dict(row)
        out['units'] = units
        price = row.get('price_cents')
        out['revenue_cents'] = None if units is None or price is None else units * price
        result.append(out)
    return result


def window(rows, lookup, request):
    """Derive revenue and rolling means over the trailing ``window`` row positions."""
    width = request.get('window', 2)
    if not isinstance(width, int) or isinstance(width, bool) or width <= 0:
        raise ValueError('window must be a positive integer')
    result = revenue(rows, lookup, request)
    for i, row in enumerate(result):
        values = [r['revenue_cents'] for r in result[max(0, i-width+1):i+1]
                  if r['revenue_cents'] is not None]
        row['roll_revenue_cents'] = sum(values) / len(values) if values else None
    return result
