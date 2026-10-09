"""Non-mutating row-table service adapters."""
from published.a00_r01 import clean, revenue, group, monthly, window
from published.a00_r01 import lookup as _lookup

# Keep the public function name distinct from its lookup-table parameter.
lookup = _lookup
__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window"]
