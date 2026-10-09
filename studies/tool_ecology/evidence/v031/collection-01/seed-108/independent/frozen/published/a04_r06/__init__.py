"""Stable row-table service entry points.

Each function accepts (rows, lookup, request) and returns a new list of
row dictionaries (or grouped output rows), without mutating inputs.
"""
from published import a04_r05 as _impl

clean = _impl.clean
revenue = _impl.revenue
group = _impl.group
monthly = _impl.monthly
lookup = _impl.lookup
window = _impl.window

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window"]
