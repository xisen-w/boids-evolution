"""Six pure-Python row-table services.

The service adapters are re-exported from the verified a05_r05 package.
"""
from published.a05_r05 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
