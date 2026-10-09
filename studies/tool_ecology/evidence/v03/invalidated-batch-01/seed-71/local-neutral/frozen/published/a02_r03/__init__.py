"""Convenient, non-mutating adapters for tabular service requests."""
from published.a00_r02 import clean, revenue, group, monthly, lookup, window

SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}

def run(family, rows, lookup_rows, request):
    """Run one named family with (rows, lookup_rows, request)."""
    try:
        service = SERVICES[family]
    except KeyError:
        raise ValueError(f"unknown family: {family!r}") from None
    return service(rows, lookup_rows, request)
