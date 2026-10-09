"""Reusable dispatcher and stable adapters for the six row-service families."""
from published.a00_r02 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    "clean": clean,
    "revenue": revenue,
    "group": group,
    "monthly": monthly,
    "lookup": lookup,
    "window": window,
}

def run(family, rows, lookup_rows, request):
    """Run one family by name; raises ValueError for unknown family names."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError("unknown service family: {!r}".format(family)) from None
    return service(rows, lookup_rows, request)

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window", "run"]
