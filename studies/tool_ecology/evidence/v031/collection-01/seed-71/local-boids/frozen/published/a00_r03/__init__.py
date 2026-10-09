"""Unified interface to the verified row-table services."""
from published.a00_r02 import clean, revenue, group, monthly, lookup_service, window

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup_service,
    'window': window,
}

def apply(family, rows, lookup, request):
    """Run one service family by name; inputs are not mutated."""
    try:
        service = _SERVICES[family]
    except KeyError:
        raise ValueError('unknown family: %s' % family) from None
    return service(rows, lookup, request)

def clean_service(rows, lookup, request): return apply('clean', rows, lookup, request)
def revenue_service(rows, lookup, request): return apply('revenue', rows, lookup, request)
def group_service(rows, lookup, request): return apply('group', rows, lookup, request)
def monthly_service(rows, lookup, request): return apply('monthly', rows, lookup, request)
def lookup_service(rows, lookup, request): return apply('lookup', rows, lookup, request)
def window_service(rows, lookup, request): return apply('window', rows, lookup, request)
