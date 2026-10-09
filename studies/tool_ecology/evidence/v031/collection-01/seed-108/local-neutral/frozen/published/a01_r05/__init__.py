"""Stable convenience exports for six row-table service adapters."""
from published.a01_r04 import (
    clean_service, revenue_service, group_service, monthly_service,
    lookup_service, window_service,
)

__all__ = ["clean_service", "revenue_service", "group_service",
           "monthly_service", "lookup_service", "window_service"]
