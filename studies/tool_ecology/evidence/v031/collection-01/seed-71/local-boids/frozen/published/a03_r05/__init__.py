"""Pure row-table service adapters backed by the verified a03_r03 package."""
from published.a03_r03 import clean, revenue, group, monthly, lookup, window
__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
