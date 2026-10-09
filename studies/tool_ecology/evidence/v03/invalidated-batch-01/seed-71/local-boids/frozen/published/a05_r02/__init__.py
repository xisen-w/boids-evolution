"""Convenient, tested adapters for row-table services.

Functions take (rows, lookup, request) and return fresh dictionaries/lists.
"""
from published.a01_r01 import clean, revenue, group, monthly, lookup as lookup_service, window

# Public check name follows service family, despite lookup's argument name.
def lookup(rows, lookup_rows, request):
    return lookup_service(rows, lookup_rows, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
