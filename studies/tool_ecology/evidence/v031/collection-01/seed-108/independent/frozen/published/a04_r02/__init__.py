"""Service adapters; delegates stable families to the prior native implementation."""
from published import a04_r01 as _base

clean = _base.clean
group = _base.group
monthly = _base.monthly
lookup = _base.lookup
window = _base.window

def revenue(rows, lookup, request):
    """Fill units and append revenue_cents without normalizing region."""
    items = _base._fill(rows, request)
    out = []
    for row in items:
        result = dict(row)
        units, price = result.get('units'), result.get('price_cents')
        result['revenue_cents'] = None if units is None or price is None else units * price
        out.append(result)
    return out
