"""Verified row services plus a batch dispatcher."""
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
    """Apply one named service; unknown names raise ValueError."""
    try:
        fn = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError('unknown family: %s' % (family,)) from None
    return fn(rows, lookup, request)

def apply_many(jobs):
    """Run jobs in order. Each job maps family, rows, lookup, request to results.

    Returns a list of results; an invalid job raises normally and stops the batch.
    Inputs are passed unchanged to the underlying non-mutating services.
    """
    return [apply(job['family'], job['rows'], job['lookup'], job['request']) for job in jobs]

def clean_service(rows, lookup, request): return apply('clean', rows, lookup, request)
def revenue_service(rows, lookup, request): return apply('revenue', rows, lookup, request)
def group_service(rows, lookup, request): return apply('group', rows, lookup, request)
def monthly_service(rows, lookup, request): return apply('monthly', rows, lookup, request)
def lookup_adapter(rows, lookup, request): return apply('lookup', rows, lookup, request)
def window_service(rows, lookup, request): return apply('window', rows, lookup, request)
