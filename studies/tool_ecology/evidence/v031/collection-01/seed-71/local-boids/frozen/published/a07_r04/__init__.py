"""Named and batch dispatch for the standard tabular row services."""
from published.a07_r02 import clean, revenue, group, monthly, lookup as lookup_service, window

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup_service,
    'window': window,
}

def process(family, rows, lookup, request):
    """Execute a service by name, raising ValueError for unknown names."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError(f'unknown service family: {family!r}') from None
    return service(rows, lookup, request)

def process_many(jobs):
    """Execute ordered jobs, each a (family, rows, lookup, request) tuple."""
    return [process(*job) for job in jobs]

def clean_adapter(rows, lookup, request): return process('clean', rows, lookup, request)
def revenue_adapter(rows, lookup, request): return process('revenue', rows, lookup, request)
def group_adapter(rows, lookup, request): return process('group', rows, lookup, request)
def monthly_adapter(rows, lookup, request): return process('monthly', rows, lookup, request)
def lookup_adapter(rows, lookup, request): return process('lookup', rows, lookup, request)
def window_adapter(rows, lookup, request): return process('window', rows, lookup, request)
