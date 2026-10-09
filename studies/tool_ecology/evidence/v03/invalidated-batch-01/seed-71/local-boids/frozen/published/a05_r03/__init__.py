"""Dependency-backed adapters for row-table service families."""
from published.a01_r01 import clean, revenue, group, monthly, window
from published.a01_r01 import lookup as _lookup

def lookup(rows, lookup_rows, request):
    """Normalize, calculate revenue, and add revenue_cents_per_target."""
    return _lookup(rows, lookup_rows, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
