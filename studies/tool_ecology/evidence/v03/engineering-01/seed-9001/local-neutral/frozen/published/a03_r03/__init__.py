"""Pure-Python table service facade backed by a verified implementation."""
from published.a02_r01 import clean, revenue, group, monthly, lookup, window

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window"]
