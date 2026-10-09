"""Reliable row-table service adapters backed by verified implementations."""
from published.a05_r02 import clean, revenue, group, monthly, window
from published.a05_r02 import lookup as _lookup

def lookup(rows, lookup_rows, request):
    """Normalize and derive revenue, then append per-target revenue ratio."""
    return _lookup(rows, lookup_rows, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
