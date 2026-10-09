"""Reusable row-table service adapters, backed by the verified a06_r02 implementation."""
from published.a06_r02 import (
    clean as clean_service,
    revenue as revenue_service,
    group as group_service,
    monthly as monthly_service,
    lookup as lookup_service,
    window as window_service,
)

# Concise public names and explicit service-adapter names are both supported.
clean = clean_service
revenue = revenue_service
group = group_service
monthly = monthly_service
lookup = lookup_service
window = window_service

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window',
           'clean_service', 'revenue_service', 'group_service', 'monthly_service',
           'lookup_service', 'window_service']
