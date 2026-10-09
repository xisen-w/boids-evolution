"""Stable public service adapters backed by the verified a00_r02 implementation."""
from published.a00_r02 import (
    clean as _clean, revenue as _revenue, group as _group,
    monthly as _monthly, lookup as _lookup, window as _window,
)

def clean(rows, lookup, request):
    """Normalize regions and fill missing units; see package README."""
    return _clean(rows, lookup, request)

def revenue(rows, lookup, request):
    """Fill units and derive revenue_cents."""
    return _revenue(rows, lookup, request)

def group(rows, lookup, request):
    """Aggregate revenue by normalized region."""
    return _group(rows, lookup, request)

def monthly(rows, lookup, request):
    """Aggregate revenue by month and normalized region."""
    return _monthly(rows, lookup, request)

def lookup_service(rows, lookup, request):
    """Add exact normalized-region revenue-per-target values."""
    return _lookup(rows, lookup, request)

def window(rows, lookup, request):
    """Add trailing row-window mean revenue."""
    return _window(rows, lookup, request)
