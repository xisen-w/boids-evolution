"""Six tested table transformation adapters."""
from published.a06_r03 import (
    clean, revenue, group, monthly, lookup_revenue, window,
    clean_service, revenue_service, group_service, monthly_service,
    lookup_service, window_service,
)

__all__ = ["clean", "revenue", "group", "monthly", "lookup_revenue", "window",
           "clean_service", "revenue_service", "group_service", "monthly_service",
           "lookup_service", "window_service"]
