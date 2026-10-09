"""Non-mutating row-service adapters backed by verified native services."""
from published import a04_r02 as _service

def clean(rows, lookup, request):
    return _service.clean(rows, lookup, request)

def revenue(rows, lookup, request):
    return _service.revenue(rows, lookup, request)

def group(rows, lookup, request):
    return _service.group(rows, lookup, request)

def monthly(rows, lookup, request):
    return _service.monthly(rows, lookup, request)

def lookup(rows, lookup_table, request):
    return _service.lookup(rows, lookup_table, request)

def window(rows, lookup, request):
    return _service.window(rows, lookup, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
