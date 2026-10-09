"""Name-based dispatcher for the six tabular service families."""
from published.a04_r05 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}

def run(family, rows, lookup_rows, request):
    """Run one family by its exact name on rows, lookup rows, and request."""
    try:
        fn = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError('unknown service family: %r' % (family,)) from None
    return fn(rows, lookup_rows, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window', 'run']
