"""Reusable tabular service adapters; implementations delegated to a02_r04."""
from published.a02_r04 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
