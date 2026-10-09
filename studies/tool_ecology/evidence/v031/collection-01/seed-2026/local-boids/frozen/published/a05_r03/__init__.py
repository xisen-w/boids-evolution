"""Non-mutating tabular service adapters."""
from published.a00_r01 import clean, revenue, group, monthly, window, _revenue_rows, _region


def lookup(rows, lookup_rows, request):
    """Add revenue per matching normalized region target; no lookup fields copied."""
    result = _revenue_rows(rows, request)
    targets = {_region(item.get('region')): item.get('target') for item in lookup_rows}
    for row in result:
        target = targets.get(_region(row.get('region')))
        value = row['revenue_cents']
        row['revenue_cents_per_target'] = (
            None if target is None or target == 0 or value is None else value / target
        )
    return result
