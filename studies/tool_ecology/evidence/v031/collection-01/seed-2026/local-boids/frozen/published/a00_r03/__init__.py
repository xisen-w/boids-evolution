"""Reliable region-normalized revenue-per-target lookup service."""
from published.a00_r02 import lookup as _lookup


def lookup(rows, lookup, request):
    """Return copied rows with normalized region, revenue, and target ratio."""
    return _lookup(rows, lookup, request)
