"""Reusable row-table service adapters and ordered multi-service execution."""
from published.a03_r02 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}


def run(family, rows, lookup_rows, request):
    """Run one named service; raise ValueError when family is unsupported."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError('unknown service family: %r' % (family,)) from None
    return service(rows, lookup_rows, request)


def run_many(families, rows, lookup_rows, request):
    """Return a dict mapping each requested family to its complete output.

    Results follow family iteration order. Duplicate names collapse as in any
    dict. Input arguments are passed through unchanged and services do not mutate them.
    """
    return {family: run(family, rows, lookup_rows, request) for family in families}


__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window', 'run', 'run_many']
