"""Stable dispatch facade over verified native tabular service adapters."""
from published.a06_r02 import clean, revenue, group, monthly, lookup, window

SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}

def run(family, rows, lookup_rows, request):
    """Run one service by name; returns that service's normal fresh result."""
    try:
        adapter = SERVICES[family]
    except KeyError:
        raise ValueError(f"unknown service family: {family!r}") from None
    return adapter(rows, lookup_rows, request)
