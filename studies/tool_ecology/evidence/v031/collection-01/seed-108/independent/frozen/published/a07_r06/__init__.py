"""Pure-Python adapters for the six tabular service families.

The implementations are reused from the declared, verified a07_r04 package.
"""
from published.a07_r04 import clean, revenue, group, monthly, lookup, window

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window"]
