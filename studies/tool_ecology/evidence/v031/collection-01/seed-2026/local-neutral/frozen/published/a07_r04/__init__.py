"""Reusable dispatch and adapters for tabular services."""
from published.a07_r03 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    "clean": clean,
    "revenue": revenue,
    "group": group,
    "monthly": monthly,
    "lookup": lookup,
    "window": window,
}

def apply(family, rows, lookup_rows, request):
    """Run one named service; raises ValueError for an unknown family."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError("unknown service family: %r" % (family,)) from None
    return service(rows, lookup_rows, request)

__all__ = ["apply", "clean", "revenue", "group", "monthly", "lookup", "window"]
