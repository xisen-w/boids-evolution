"""Verified reusable table service adapters."""
from published import a04_r01 as _core
from published import a01_r01 as _lookup_core

clean = _core.clean
revenue = _core.revenue
group = _core.group
monthly = _core.monthly
window = _core.window
# Use the separately verified lookup implementation; adapters are stateless.
def lookup(rows, lookup, request):
    return _lookup_core.lookup(rows, lookup, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
