"""Row-oriented transformations for the recurring table service families.

All adapters return fresh row dictionaries (or fresh aggregate dictionaries) and
leave their inputs untouched. Implementations are provided by published.a04_r02.
"""
from published.a04_r02 import clean, revenue, group, monthly, lookup, window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
