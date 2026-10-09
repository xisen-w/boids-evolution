"""Reusable row-table service adapters, backed by the verified a04_r02 implementation."""
from published import a04_r02 as _impl

clean = _impl.clean
revenue = _impl.revenue
group = _impl.group
monthly = _impl.monthly
lookup = _impl.lookup
window = _impl.window
