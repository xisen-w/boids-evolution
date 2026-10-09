"""Stable native-Python row-table service adapters."""
from published.a03_r04 import clean_service, revenue_service, group_service, monthly_service, lookup_service, window_service

clean = clean_service
revenue = revenue_service
group = group_service
monthly = monthly_service
lookup = lookup_service
window = window_service

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window', 'clean_service', 'revenue_service', 'group_service', 'monthly_service', 'lookup_service', 'window_service']
