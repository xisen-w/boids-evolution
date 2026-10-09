"""Composable adapters for the six recurring row-table services.

Implementations are reused from the verified dependency published.a06_r02.
"""
from published.a06_r02 import clean, revenue, group, monthly, lookup, window

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window"]
