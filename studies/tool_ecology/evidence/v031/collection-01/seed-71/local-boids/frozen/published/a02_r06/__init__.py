"""Row-table service adapters and convenient family dispatch."""
from published.a07_r03 import (
    clean_adapter as clean,
    revenue_adapter as revenue,
    group_adapter as group,
    monthly_adapter as monthly,
    lookup_adapter as lookup_service,
    window_adapter as window,
)

_SERVICES = {
    "clean": clean,
    "revenue": revenue,
    "group": group,
    "monthly": monthly,
    "lookup": lookup_service,
    "window": window,
}

def process(family, rows, lookup, request):
    """Run one named family on row dictionaries, lookup rows and request."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError(f"unknown service family: {family!r}") from None
    return service(rows, lookup, request)

def process_many(families, rows, lookup, request):
    """Run several families; return a dict keyed in the requested order.

    Each family is executed independently. Inputs are passed unchanged to the
    adapters; as with the individual services, they must not be mutated.
    """
    return {family: process(family, rows, lookup, request) for family in families}
