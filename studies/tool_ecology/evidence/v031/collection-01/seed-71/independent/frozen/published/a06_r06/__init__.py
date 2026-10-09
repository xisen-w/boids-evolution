"""Six reusable table-service adapters, backed by the verified a06_r02 package."""
from published.a06_r02 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
