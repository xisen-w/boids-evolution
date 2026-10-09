"""Convenient tabular service adapters and ordered batch dispatch."""
from published.a04_r05 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    "clean": clean, "revenue": revenue, "group": group,
    "monthly": monthly, "lookup": lookup, "window": window,
}

def run_service(family, rows, lookup_rows, request):
    """Run one named service; unknown family names raise ValueError."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError("unknown service family: {!r}".format(family)) from None
    return service(rows, lookup_rows, request)

def run_many(jobs):
    """Run ordered (family, rows, lookup_rows, request) jobs; return results."""
    return [run_service(family, rows, lookup_rows, request)
            for family, rows, lookup_rows, request in jobs]

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window", "run_service", "run_many"]
