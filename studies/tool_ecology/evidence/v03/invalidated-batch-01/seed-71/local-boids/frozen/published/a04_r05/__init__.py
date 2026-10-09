"""Convenient row-service adapters and multi-family dispatch."""
from published.a06_r03 import transform as _transform

_FAMILIES = ("clean", "revenue", "group", "monthly", "lookup", "window")

def transform(family, rows, lookup, request):
    """Run one service family; unknown family names raise KeyError."""
    return _transform(family, rows, lookup, request)

def transform_many(families, rows, lookup, request):
    """Return {family: result} for requested family names, preserving order.

    Each service receives the same inputs. Services do not mutate them.
    Duplicate names naturally collapse to one dictionary entry.
    """
    return {family: transform(family, rows, lookup, request) for family in families}

def clean(rows, lookup, request): return transform("clean", rows, lookup, request)
def revenue(rows, lookup, request): return transform("revenue", rows, lookup, request)
def group(rows, lookup, request): return transform("group", rows, lookup, request)
def monthly(rows, lookup, request): return transform("monthly", rows, lookup, request)
def lookup(rows, lookup_rows, request): return transform("lookup", rows, lookup_rows, request)
def window(rows, lookup, request): return transform("window", rows, lookup, request)
