"""Reusable row-table services; see README for adapter contracts."""
from published.a07_r02 import clean, revenue, group, monthly, window
from published.a07_r02 import _prepare, _region

def lookup(rows, lookup, request):
    """Derive revenue and append per-target revenue using normalized region keys."""
    data = _prepare(rows, request)
    targets = {}
    for item in lookup:
        key = _region(item.get('region'))
        if key is not None:
            targets[key] = item.get('target')
    for row in data:
        key = row.get('region')
        target = targets.get(key) if key is not None else None
        amount = row.get('revenue_cents')
        row['revenue_cents_per_target'] = None if target is None or target == 0 or amount is None else amount / target
    return data
