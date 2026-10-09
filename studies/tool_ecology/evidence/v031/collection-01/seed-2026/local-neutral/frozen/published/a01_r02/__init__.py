"""Table transformation service adapters."""
from statistics import mean, median
from published.a01_r01 import revenue, group, monthly, lookup, window

def clean(rows, lookup, request):
    """Copy rows, normalize region, and fill missing units without deriving fields."""
    result = [dict(row) for row in rows]
    present = [row.get('units') for row in result if row.get('units') is not None]
    mode = request.get('fill', 'zero')
    fill = 0 if not present or mode == 'zero' else mean(present) if mode == 'mean' else median(present)
    for row in result:
        if row.get('region') is not None:
            row['region'] = row['region'].strip().lower()
        if row.get('units') is None:
            row['units'] = fill
    return result
