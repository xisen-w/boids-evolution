"""Stable adapters for reusable row-table services.

Each service accepts (rows, lookup, request), returns fresh dictionaries, and
leaves caller-owned inputs unchanged. See README.md for behavior.
"""
from published.a05_r03 import clean, revenue, group, monthly, window
from published.a05_r03 import lookup as lookup_service

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup_service', 'window']
