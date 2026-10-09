"""Reusable adapters for the six tabular service families.

Functions accept (rows, lookup, request), return fresh results, and leave inputs untouched.
"""
from published.a01_r03 import clean, revenue, group, monthly, lookup as lookup_service, window

# Public family name `lookup` intentionally shadows the input argument name used in API docs.
lookup = lookup_service
__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
