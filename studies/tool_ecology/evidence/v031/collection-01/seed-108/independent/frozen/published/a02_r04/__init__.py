"""Row-table service adapters backed by the verified a02_r02 implementation."""
from published.a02_r02 import clean, revenue, group, monthly, lookup, window

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window"]
