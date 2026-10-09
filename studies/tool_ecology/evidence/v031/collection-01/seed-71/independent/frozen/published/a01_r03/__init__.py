"""Convenience service adapters backed by the verified a01_r02 implementation."""
from published.a01_r02 import (
    clean as clean_check,
    revenue as revenue_check,
    group as group_check,
    monthly as monthly_check,
    lookup as lookup_check,
    window as window_check,
)

# Public concise APIs and explicit service-check adapters are equivalent.
clean = clean_check
revenue = revenue_check
group = group_check
monthly = monthly_check
lookup = lookup_check
window = window_check

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window",
           "clean_check", "revenue_check", "group_check", "monthly_check",
           "lookup_check", "window_check"]
