"""Named dispatcher for reusable row-table service adapters."""
from published.a07_r03 import (
    clean_adapter, revenue_adapter, group_adapter, monthly_adapter,
    lookup_adapter, window_adapter,
)

_SERVICES = {
    "clean": clean_adapter,
    "revenue": revenue_adapter,
    "group": group_adapter,
    "monthly": monthly_adapter,
    "lookup": lookup_adapter,
    "window": window_adapter,
}

def process(family, rows, lookup, request):
    """Dispatch by family name; raises ValueError for unsupported names."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError(f"unknown service family: {family!r}") from None
    return service(rows, lookup, request)
