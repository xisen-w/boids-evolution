"""Stable row-table service adapters backed by the verified a05_r01 implementation."""
from published.a05_r01 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
