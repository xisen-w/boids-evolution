"""Stable public adapters for row-oriented tabular transformations.

Implementations are delegated to the verified pure-Python a04_r02 package.
"""
from published.a04_r02 import clean, revenue, group, monthly, lookup, window

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window"]
