"""Stable entry points for row-table transformation services."""
from published import a04_r03 as _impl

clean = _impl.clean
revenue = _impl.revenue
group = _impl.group
monthly = _impl.monthly
lookup = _impl.lookup
window = _impl.window

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window"]
