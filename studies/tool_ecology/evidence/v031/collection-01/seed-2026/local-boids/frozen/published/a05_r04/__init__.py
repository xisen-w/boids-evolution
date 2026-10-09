"""Stable adapters for six tabular service families."""
from published.a04_r02 import clean, revenue, group, monthly, window

# Keep lookup local to ensure normalized matching and explicit missing-target handling.
def lookup(rows, lookup, request):
    from published.a04_r02 import _derive
    out = _derive(rows, request, True)
    targets = {}
    for item in lookup:
        key = item.get('region')
        if isinstance(key, str):
            targets[key.strip().lower()] = item.get('target')
    for row in out:
        target = targets.get(row.get('region'))
        value = row['revenue_cents']
        row['revenue_cents_per_target'] = None if target is None or target == 0 or value is None else value / target
    return out

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
