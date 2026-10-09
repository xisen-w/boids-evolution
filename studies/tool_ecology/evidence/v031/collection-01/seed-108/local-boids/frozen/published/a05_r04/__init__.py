"""Pure row-table service adapters backed by the verified reference package."""
from published.a00_r01 import clean, revenue, group, monthly, window
from published.a00_r01 import lookup as lookup_service

lookup = lookup_service
__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window"]
