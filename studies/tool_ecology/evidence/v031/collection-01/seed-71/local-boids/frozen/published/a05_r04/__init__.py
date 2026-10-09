"""Small, dependency-backed facade for six row-table service operations."""
from published import a04_r02 as _impl

def clean(rows, lookup, request):
    return _impl.clean(rows, lookup, request)

def revenue(rows, lookup, request):
    return _impl.revenue(rows, lookup, request)

def group(rows, lookup, request):
    return _impl.group(rows, lookup, request)

def monthly(rows, lookup, request):
    return _impl.monthly(rows, lookup, request)

def lookup(rows, lookup_table, request):
    return _impl.lookup(rows, lookup_table, request)

def window(rows, lookup, request):
    return _impl.window(rows, lookup, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
