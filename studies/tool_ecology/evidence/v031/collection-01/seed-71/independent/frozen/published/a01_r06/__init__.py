"""Stable public service API, backed by the verified a01_r05 implementation."""
from published.a01_r05 import clean, revenue, group, monthly, lookup, window

clean_check = clean
revenue_check = revenue
group_check = group
monthly_check = monthly
lookup_check = lookup
window_check = window

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window",
           "clean_check", "revenue_check", "group_check", "monthly_check",
           "lookup_check", "window_check"]
