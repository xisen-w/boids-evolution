"""Table service adapters and multi-service dispatcher."""
from published.a04_r05 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}

def run_many(families, rows, lookup_rows, request):
    """Return {family: result} for requested services, preserving family order.

    Each service independently receives the original inputs; no result is fed
    into another service. Duplicate family names naturally collapse in output.
    """
    result = {}
    for family in families:
        try:
            service = _SERVICES[family]
        except (KeyError, TypeError):
            raise ValueError('unknown service family: %r' % (family,)) from None
        result[family] = service(rows, lookup_rows, request)
    return result

def clean_service(rows, lookup_rows, request):
    return clean(rows, lookup_rows, request)
def revenue_service(rows, lookup_rows, request):
    return revenue(rows, lookup_rows, request)
def group_service(rows, lookup_rows, request):
    return group(rows, lookup_rows, request)
def monthly_service(rows, lookup_rows, request):
    return monthly(rows, lookup_rows, request)
def lookup_service(rows, lookup_rows, request):
    return lookup(rows, lookup_rows, request)
def window_service(rows, lookup_rows, request):
    return window(rows, lookup_rows, request)

__all__ = ['clean_service', 'revenue_service', 'group_service', 'monthly_service',
           'lookup_service', 'window_service', 'run_many']
