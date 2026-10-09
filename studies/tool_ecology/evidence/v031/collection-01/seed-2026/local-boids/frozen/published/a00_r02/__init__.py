"""Focused, reusable region-normalized revenue target lookup."""
from published.a03_r01 import lookup_rate as _lookup_rate


def lookup(rows, lookup, request):
    """Return copied rows with normalized regions, filled units, revenue and target ratio."""
    return _lookup_rate(rows, lookup, request)
