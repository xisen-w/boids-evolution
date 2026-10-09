"""Small stable facade for the six row-table service families."""
from published.a03_r04 import clean, revenue, group, monthly, lookup, window, transform

# Explicit adapter names make the publication interface self-describing.
clean_service = clean
revenue_service = revenue
group_service = group
monthly_service = monthly
lookup_service = lookup
window_service = window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window',
           'transform', 'clean_service', 'revenue_service', 'group_service',
           'monthly_service', 'lookup_service', 'window_service']
