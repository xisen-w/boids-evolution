"""Verified row-oriented sales table services.

All service functions accept (rows, lookup, request), return fresh row mappings,
and do not mutate arguments. See README.md for behavior and parameters.
"""
from published.a07_r04 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
