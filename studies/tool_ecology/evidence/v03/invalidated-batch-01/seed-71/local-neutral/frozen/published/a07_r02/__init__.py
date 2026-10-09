"""Row-oriented sales table utilities, based on the tested a07_r01 implementation."""
from published.a07_r01 import clean, group, monthly, lookup, window
from published.a07_r01 import _fill_value

def revenue(rows, lookup, request):
    """Copy rows, fill absent units, and derive revenue_cents without changing region."""
    fill = _fill_value(rows, request.get('fill', 'zero'))
    out = []
    for original in rows:
        row = dict(original)
        if row.get('units') is None:
            row['units'] = fill
        units, price = row.get('units'), row.get('price_cents')
        row['revenue_cents'] = None if units is None or price is None else units * price
        out.append(row)
    return out

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
