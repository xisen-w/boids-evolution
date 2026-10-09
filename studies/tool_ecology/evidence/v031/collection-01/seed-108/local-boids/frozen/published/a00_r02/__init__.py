"""Stable public adapters for common row-table transformations."""
from published.a00_r01 import (
    clean as clean,
    revenue as revenue,
    group as group,
    monthly as monthly,
    lookup as lookup,
    window as window,
)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
