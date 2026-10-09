"""Stable root-level adapters for the six tabular services."""
from published.a02_r01 import (
    clean as _clean, revenue as _revenue, group as _group,
    monthly as _monthly, lookup as _lookup, window as _window,
)

def clean(rows, lookup, request):
    return _clean(rows, lookup, request)

def revenue(rows, lookup, request):
    return _revenue(rows, lookup, request)

def group(rows, lookup, request):
    return _group(rows, lookup, request)

def monthly(rows, lookup, request):
    return _monthly(rows, lookup, request)

def lookup(rows, lookup_rows, request):
    return _lookup(rows, lookup_rows, request)

def window(rows, lookup, request):
    return _window(rows, lookup, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
