"""Stable root adapters for six tabular transformation services."""
from published.a01_r03 import clean as _clean, revenue as _revenue, group as _group
from published.a01_r03 import monthly as _monthly, lookup as _lookup, window as _window

def clean(rows, lookup_rows, request):
    return _clean(rows, lookup_rows, request)

def revenue(rows, lookup_rows, request):
    return _revenue(rows, lookup_rows, request)

def group(rows, lookup_rows, request):
    return _group(rows, lookup_rows, request)

def monthly(rows, lookup_rows, request):
    return _monthly(rows, lookup_rows, request)

def lookup(rows, lookup_rows, request):
    return _lookup(rows, lookup_rows, request)

def window(rows, lookup_rows, request):
    return _window(rows, lookup_rows, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
