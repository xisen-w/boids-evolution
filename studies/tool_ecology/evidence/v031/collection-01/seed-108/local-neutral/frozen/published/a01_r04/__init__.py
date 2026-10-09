"""Row-table service adapters.

Each service accepts (rows, lookup, request) and returns fresh row dictionaries
or grouped result dictionaries. Implementations are re-exported from the tested
a01_r02 dependency.
"""
from published.a01_r02 import (
    clean_service, revenue_service, group_service, monthly_service,
    lookup_service, window_service,
)

__all__ = ["clean_service", "revenue_service", "group_service",
           "monthly_service", "lookup_service", "window_service"]
