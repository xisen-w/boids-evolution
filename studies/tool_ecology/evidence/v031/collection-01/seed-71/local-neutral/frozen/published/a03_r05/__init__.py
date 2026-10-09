"""Stable convenience API for sales-table transformations.

Implementation is reused from the verified a03_r04 package.
"""
from published.a03_r04 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
