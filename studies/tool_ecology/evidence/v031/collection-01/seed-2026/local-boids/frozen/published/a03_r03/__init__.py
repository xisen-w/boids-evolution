"""Row-table services with normalized-key lookup."""
from published.a00_r01 import clean, revenue, group, monthly, window

def lookup(rows, lookup, request):
    """Derive revenue and append ratio against normalized region targets."""
    data = revenue(rows, lookup, request)
    targets = {}
    for item in lookup:
        key = item.get('region')
        key = key.strip().lower() if isinstance(key, str) else key
        targets[key] = item.get('target')
    for row in data:
        key = row.get('region')
        key = key.strip().lower() if isinstance(key, str) else key
        target = targets.get(key)
        amount = row.get('revenue_cents')
        row['revenue_cents_per_target'] = None if target is None or target == 0 or amount is None else amount / target
    return data

lookup_service = lookup
