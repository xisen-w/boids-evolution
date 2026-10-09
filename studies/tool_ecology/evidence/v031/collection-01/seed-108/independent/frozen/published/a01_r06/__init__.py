"""Stable dispatch and direct adapters for six table services."""
from published.a01_r02 import clean, revenue, group, monthly, lookup as lookup_service, window

_SERVICES = {
    "clean": clean,
    "revenue": revenue,
    "group": group,
    "monthly": monthly,
    "lookup": lookup_service,
    "window": window,
}

def run(family, rows, lookup, request):
    """Run one named service; family must be one of the six supported names."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError("unknown family: %r" % (family,))
    return service(rows, lookup, request)

__all__ = ["clean", "revenue", "group", "monthly", "lookup_service", "window", "run"]
