"""Stable public adapters for the six table-service transformations.

The implementation is supplied by the dependency-free, service-verified
published.a00_r02 package.
"""
from published.a00_r02 import clean, revenue, group, monthly, window
from published.a00_r02 import lookup as _lookup


def lookup_service(rows, lookup, request):
    """Normalize rows, derive revenue and revenue per regional target."""
    return _lookup(rows, lookup, request)
