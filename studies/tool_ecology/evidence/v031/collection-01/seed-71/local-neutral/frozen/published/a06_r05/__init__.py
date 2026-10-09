"""Stable table-service facade backed by the tested a06_r04 implementation."""
from published.a06_r04 import (
    clean, revenue, group, monthly, lookup_revenue, window,
    clean_service, revenue_service, group_service, monthly_service,
    lookup_service, window_service,
)

__all__ = ["clean", "revenue", "group", "monthly", "lookup_revenue", "window",
           "clean_service", "revenue_service", "group_service", "monthly_service",
           "lookup_service", "window_service"]
