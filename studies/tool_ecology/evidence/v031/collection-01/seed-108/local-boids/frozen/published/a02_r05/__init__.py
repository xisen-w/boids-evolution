"""Convenient dispatch for the six row-table service families."""
from published.a00_r01 import clean, revenue, group, monthly, window
from published.a00_r01 import lookup_service as lookup

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}

def apply(family, rows, lookup_rows, request):
    """Run one named service; raises ValueError for an unknown family."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError(f'unknown service family: {family!r}') from None
    return service(rows, lookup_rows, request)

__all__ = ['apply', 'clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
