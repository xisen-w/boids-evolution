"""Verified table-service adapters, re-exported with a name dispatcher."""
from published.a06_r05 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}

def apply(service, rows, lookup_rows, request):
    """Dispatch one of the six services; unknown names raise ValueError."""
    try:
        fn = _SERVICES[service]
    except (KeyError, TypeError):
        raise ValueError('unknown service: {!r}'.format(service)) from None
    return fn(rows, lookup_rows, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window', 'apply']
