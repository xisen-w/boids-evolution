"""Row-service adapters and a family-selecting dispatcher."""
from published.a06_r03 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    "clean": clean,
    "revenue": revenue,
    "group": group,
    "monthly": monthly,
    "lookup": lookup,
    "window": window,
}

def run_service(family, rows, lookup_rows, request):
    """Run one named service with (rows, lookup_rows, request) arguments.

    Raises KeyError for an unsupported family. Inputs follow the documented
    recurring row-service schema; semantics are provided by a verified dependency.
    """
    return _SERVICES[family](rows, lookup_rows, request)

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window", "run_service"]
