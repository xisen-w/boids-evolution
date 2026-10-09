"""Six non-mutating table transformation services.

The public functions accept (rows, lookup_rows, request) and return new lists.
"""
from published.a07_r05 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
