"""Composable dispatch for the six standard tabular service adapters."""
from published.a07_r02 import clean, revenue, group, monthly, lookup as lookup_service, window

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup_service,
    'window': window,
}

def process(family, rows, lookup_rows, request):
    """Run one named service; raises ValueError for an unknown family."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError(f'unknown service family: {family!r}') from None
    return service(rows, lookup_rows, request)

def clean_adapter(rows, lookup, request):
    return process('clean', rows, lookup, request)
def revenue_adapter(rows, lookup, request):
    return process('revenue', rows, lookup, request)
def group_adapter(rows, lookup, request):
    return process('group', rows, lookup, request)
def monthly_adapter(rows, lookup, request):
    return process('monthly', rows, lookup, request)
def lookup_adapter(rows, lookup, request):
    return process('lookup', rows, lookup, request)
def window_adapter(rows, lookup, request):
    return process('window', rows, lookup, request)
