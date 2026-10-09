"""Stable row-table transformation adapters plus a family dispatcher."""
from published.a06_r02 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    "clean": clean,
    "revenue": revenue,
    "group": group,
    "monthly": monthly,
    "lookup": lookup,
    "window": window,
}

def transform(family, rows, lookup_rows, request):
    """Run one named service family; raises KeyError for unknown family."""
    return _SERVICES[family](rows, lookup_rows, request)
