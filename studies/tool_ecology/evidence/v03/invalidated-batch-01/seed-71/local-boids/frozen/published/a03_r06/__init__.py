"""Selective dispatch for sales-table service views."""
from published.a01_r01 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    'clean': clean,
    'revenue': revenue,
    'group': group,
    'monthly': monthly,
    'lookup': lookup,
    'window': window,
}


def run(rows, lookup_rows, request, families=None):
    """Return requested service results keyed by family; default to all six.

    Unlike calling every service, selecting families only requires parameters
    used by those services. The input objects are passed to the verified,
    non-mutating a01_r01 implementations.
    """
    selected = tuple(_SERVICES) if families is None else tuple(families)
    unknown = set(selected) - _SERVICES.keys()
    if unknown:
        raise ValueError('unknown service family: ' + ', '.join(sorted(unknown)))
    return {name: _SERVICES[name](rows, lookup_rows, request) for name in selected}


def clean_adapter(rows, lookup, request):
    return clean(rows, lookup, request)

def revenue_adapter(rows, lookup, request):
    return revenue(rows, lookup, request)

def group_adapter(rows, lookup, request):
    return group(rows, lookup, request)

def monthly_adapter(rows, lookup, request):
    return monthly(rows, lookup, request)

def lookup_adapter(rows, lookup, request):
    return globals()['lookup'](rows, lookup, request)

def window_adapter(rows, lookup, request):
    return window(rows, lookup, request)
