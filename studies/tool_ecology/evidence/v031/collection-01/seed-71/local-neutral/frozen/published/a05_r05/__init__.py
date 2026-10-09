"""Stable adapters for the six tabular service families."""
from published import a05_r04 as _impl

clean = _impl.clean
revenue = _impl.revenue
group = _impl.group
monthly = _impl.monthly
window = _impl.window
lookup = _impl.lookup

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
