"""Stable, dependency-backed API for row-oriented table services."""
from published.a07_r05 import clean, revenue, group, monthly, window
from published.a07_r05 import lookup as _lookup

def lookup(rows, lookup, request):
    """Return rows enriched with revenue per matching region target."""
    return _lookup(rows, lookup, request)
