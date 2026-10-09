"""Six row transformation services, delegated to the verified a07_r05 API."""
from published.a07_r05 import clean, revenue, group, monthly, lookup, window
__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window"]
