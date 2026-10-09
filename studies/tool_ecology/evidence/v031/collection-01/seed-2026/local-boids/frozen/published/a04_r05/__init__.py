"""Table operations and a name-based dispatcher."""
from published.a04_r04 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}

def run(family, rows, lookup_rows, request):
    """Dispatch a service by family name; unknown names raise ValueError."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError('unknown service family: %r' % (family,)) from None
    return service(rows, lookup_rows, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window', 'run']
