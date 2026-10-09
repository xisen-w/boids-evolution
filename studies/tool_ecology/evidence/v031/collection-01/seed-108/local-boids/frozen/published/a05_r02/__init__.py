"""Stable concise facade for the six row-table transformation services.

All adapters accept (rows, lookup, request), and delegate to the verified
implementation in published.a00_r01 without modifying caller-owned inputs.
"""
from published.a00_r01 import clean, revenue, group, monthly, lookup as lookup_service, window

# Expose the family name as a Python-callable API.
lookup = lookup_service

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
