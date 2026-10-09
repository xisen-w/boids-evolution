"""Stable six-family row-service facade, delegated to verified native services."""
from published import a04_r02 as _services

# Keep explicit root-level adapters for publication service discovery.
def clean(rows, lookup, request):
    return _services.clean(rows, lookup, request)

def revenue(rows, lookup, request):
    return _services.revenue(rows, lookup, request)

def group(rows, lookup, request):
    return _services.group(rows, lookup, request)

def monthly(rows, lookup, request):
    return _services.monthly(rows, lookup, request)

def lookup(rows, lookup_table, request):
    return _services.lookup(rows, lookup_table, request)

def window(rows, lookup, request):
    return _services.window(rows, lookup, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
