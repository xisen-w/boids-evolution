"""Sales-table service transformations with immutable-input semantics.

Public adapters have signature ``(rows, lookup, request)``. See README.md.
"""
from published.a05_r04 import clean, revenue, group, monthly, window
from published.a05_r04 import lookup_service as lookup

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
