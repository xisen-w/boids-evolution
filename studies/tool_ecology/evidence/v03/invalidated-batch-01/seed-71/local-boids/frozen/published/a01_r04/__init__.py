"""Stable, non-mutating adapters for common sales-table transformations."""
from published.a01_r03 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
