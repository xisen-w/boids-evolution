"""Reliable row-table service adapters, reusing verified native transformations."""
from published.a00_r01 import clean, revenue, group, monthly, window
from published.a00_r01 import _revenue_rows, _region


def lookup(rows, lookup_rows, request):
    """Derive revenue and exact-key revenue/target without adding lookup fields."""
    data = _revenue_rows(rows, request)
    targets = {entry.get('region'): entry.get('target') for entry in lookup_rows}
    for row in data:
        target = targets.get(_region(row.get('region')))
        value = row['revenue_cents']
        row['revenue_cents_per_target'] = (
            None if target is None or target == 0 or value is None else value / target
        )
    return data
