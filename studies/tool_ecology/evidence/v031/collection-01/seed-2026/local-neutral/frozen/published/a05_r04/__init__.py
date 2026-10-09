"""Stable service adapters for sales-row transformations."""
from published.a05_r01 import clean, revenue, group, monthly, window
from published.a05_r01 import lookup as _lookup


def lookup_service(rows, lookup, request):
    """Append revenue per exact normalized-region target to fresh row copies."""
    return _lookup(rows, lookup, request)
