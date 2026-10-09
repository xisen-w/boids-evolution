"""Stable convenience dispatch over verified native row-table services."""
from published.a01_r01 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    'clean': clean, 'revenue': revenue, 'group': group,
    'monthly': monthly, 'lookup': lookup, 'window': window,
}

def run(family, rows, lookup_rows, request):
    """Run one family adapter; unknown family names raise ValueError."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError('unknown family: %r' % (family,)) from None
    return service(rows, lookup_rows, request)
