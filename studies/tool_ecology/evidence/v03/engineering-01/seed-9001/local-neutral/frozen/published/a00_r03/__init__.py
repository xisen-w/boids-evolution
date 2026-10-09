"""Stable, explicit service facade over the verified a00_r02 implementations."""
from published.a00_r02 import clean as _clean, revenue as _revenue, group as _group
from published.a00_r02 import monthly as _monthly, lookup as _lookup, window as _window

def serve_clean(rows, lookup, request):
    return _clean(rows, lookup, request)

def serve_revenue(rows, lookup, request):
    return _revenue(rows, lookup, request)

def serve_group(rows, lookup, request):
    return _group(rows, lookup, request)

def serve_monthly(rows, lookup, request):
    return _monthly(rows, lookup, request)

def serve_lookup(rows, lookup, request):
    return _lookup(rows, lookup, request)

def serve_window(rows, lookup, request):
    return _window(rows, lookup, request)

SERVICES = {
    'clean': serve_clean, 'revenue': serve_revenue, 'group': serve_group,
    'monthly': serve_monthly, 'lookup': serve_lookup, 'window': serve_window,
}
