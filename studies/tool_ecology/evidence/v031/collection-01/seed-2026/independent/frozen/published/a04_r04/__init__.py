"""Reusable tabular service adapters, backed by the verified a04_r01 package."""
from published.a04_r01 import clean, revenue, group, monthly, lookup, window

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window"]
