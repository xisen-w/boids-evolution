"""Convenient stable import surface for the six verified table services.

Implementations are provided by the received, service-tested a03_r02 package.
"""
from published.a03_r02 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
