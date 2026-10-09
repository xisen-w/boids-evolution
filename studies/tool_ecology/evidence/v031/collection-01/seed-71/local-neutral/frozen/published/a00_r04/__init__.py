"""Reusable adapters for six recurring tabular services."""
from published.a00_r02 import clean as _clean, revenue as _revenue, group as _group, monthly as _monthly, lookup as _lookup, window as _window

def clean(rows, lookup, request):
    """Normalize regions and fill missing units; preserve row/column order."""
    return _clean(rows, lookup, request)

def revenue(rows, lookup, request):
    """Fill units and append revenue_cents to every row."""
    return _revenue(rows, lookup, request)

def group(rows, lookup, request):
    """Aggregate revenue by normalized region, dropping missing keys."""
    return _group(rows, lookup, request)

def monthly(rows, lookup, request):
    """Aggregate revenue by YYYY-MM and normalized region."""
    return _monthly(rows, lookup, request)

def lookup_service(rows, lookup, request):
    """Append per-target revenue using normalized region-key lookup."""
    return _lookup(rows, lookup, request)

def window(rows, lookup, request):
    """Append trailing ROWS-window mean revenue."""
    return _window(rows, lookup, request)
