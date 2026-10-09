"""Reusable row-table transformations; implementations delegated to a verified native package."""
from published.a06_r02 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}

def run(family, rows, lookup_rows, request):
    """Run one supported service family; unsupported names raise ValueError."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError('unsupported service family: %r' % (family,))
    return service(rows, lookup_rows, request)
