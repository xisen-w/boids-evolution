"""Native dispatch and batch helpers for recurring row-table services."""
from published.a06_r02 import clean, revenue, group, monthly, lookup, window

_SERVICES = {name: fn for name, fn in (
    ('clean', clean), ('revenue', revenue), ('group', group),
    ('monthly', monthly), ('lookup', lookup), ('window', window))}


def run(family, rows, lookup_rows, request):
    """Execute one service family; raises ValueError for unknown family."""
    try:
        fn = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError('unsupported service family: %r' % (family,))
    return fn(rows, lookup_rows, request)


def run_many(families, rows, lookup_rows, request):
    """Return {family: result} for requested names, preserving their order.

    Each service receives the same inputs; delegated services must not mutate them.
    Duplicate family names naturally collapse to the last identical result.
    """
    return {family: run(family, rows, lookup_rows, request) for family in families}

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window', 'run', 'run_many']
