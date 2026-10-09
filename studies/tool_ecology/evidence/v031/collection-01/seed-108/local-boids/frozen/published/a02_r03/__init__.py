"""Six non-mutating row-table service adapters backed by published.a00_r01."""
from published.a00_r01 import clean, revenue, group, monthly, window
from published.a00_r01 import lookup as _lookup
lookup = _lookup
__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
