"""Unified dispatcher and adapters for the row-table service families."""
from published.a06_r02 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    "clean": clean,
    "revenue": revenue,
    "group": group,
    "monthly": monthly,
    "lookup": lookup,
    "window": window,
}

def run(family, rows, lookup_rows, request):
    """Run a named service on rows, lookup_rows and request; unknown family raises KeyError."""
    return _SERVICES[family](rows, lookup_rows, request)
