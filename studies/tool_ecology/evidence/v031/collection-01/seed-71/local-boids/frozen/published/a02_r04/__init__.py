"""Verified row-table services exposed through a concise family dispatcher."""
from published.a07_r03 import (
    clean_adapter as clean,
    revenue_adapter as revenue,
    group_adapter as group,
    monthly_adapter as monthly,
    lookup_adapter as lookup_service,
    window_adapter as window,
)

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup_service,
    'window': window,
}

def process(family, rows, lookup, request):
    """Run a service family on (rows, lookup rows, request); reject unknown names."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError(f'unknown service family: {family!r}') from None
    return service(rows, lookup, request)
