"""Verified row-table services, delegated to the immutable a00_r01 implementation."""
from published.a00_r01 import clean, revenue, group, monthly, lookup, window

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window"]
