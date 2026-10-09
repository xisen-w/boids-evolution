"""Verified lookup transformation adapter."""
from published.a02_r01 import lookup as _lookup


def lookup(rows, lookup, request):
    """Return copied rows with normalized revenue and target-normalized revenue."""
    return _lookup(rows, lookup, request)
