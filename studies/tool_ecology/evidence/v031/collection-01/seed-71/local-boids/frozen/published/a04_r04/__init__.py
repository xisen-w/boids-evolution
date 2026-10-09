"""Stable round-three facade for row-oriented table transformations.

The implementation is delegated to the verified a04_r02 package.
"""
from published.a04_r02 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
