"""Composable row-table service adapters and dispatcher."""
from published.a01_r01 import clean, revenue, group, monthly, window
from published.a01_r01 import lookup as _lookup


def lookup(rows, lookup_rows, request):
    """Return normalized rows with revenue per region target."""
    return _lookup(rows, lookup_rows, request)


_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}


def run(family, rows, lookup_rows, request):
    """Run one named service; raises ValueError for an unknown family."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError(f"unknown service family: {family!r}") from None
    return service(rows, lookup_rows, request)


__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window', 'run']
