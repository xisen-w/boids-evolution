"""Row-table services re-exported through a stable family dispatcher."""
from published.a03_r04 import clean, revenue, group, monthly, lookup, window, transform

# Explicit adapters provide uniform host-facing signatures.
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

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window', 'transform',
           'clean_service', 'revenue_service', 'group_service', 'monthly_service',
           'lookup_service', 'window_service']
