"""Tabular service adapters plus ordered multi-service dispatch."""
from published.a02_r04 import clean, revenue, group, monthly, lookup, window, run_service

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window", "run_service", "run_many"]

def run_many(jobs):
    """Evaluate ordered jobs of (family, rows, lookup_rows, request).

    Returns results in job order. Each job uses the same semantics as run_service.
    Raises ValueError on an unsupported family; other service errors propagate.
    """
    return [run_service(family, rows, lookup_rows, request)
            for family, rows, lookup_rows, request in jobs]
