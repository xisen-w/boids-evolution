"""Dispatchable row-table data services."""
from published.a04_r02 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}

def run(family, rows, lookup_rows, request):
    """Run a named service family; raise ValueError for an unknown family."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError('unknown family: %r' % (family,)) from None
    return service(rows, lookup_rows, request)

__all__ = ['run', 'clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
