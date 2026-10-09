"""Stable, namespaced entry points for six row-table services.

Implementations are reused from the verified a02_r02 publication.
"""
from published.a02_r02 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
