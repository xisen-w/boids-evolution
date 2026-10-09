"""Non-mutating row-table services backed by published a07_r04."""
from published.a07_r04 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
