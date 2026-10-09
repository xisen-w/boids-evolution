"""Six table transformations plus a small name-based dispatch helper."""
from published.a06_r04 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}

def apply(service, rows, lookup_rows, request):
    """Run a supported service by name; raise ValueError for unknown names."""
    try:
        fn = _SERVICES[service]
    except (KeyError, TypeError):
        raise ValueError('unknown service: {!r}'.format(service)) from None
    return fn(rows, lookup_rows, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window', 'apply']
