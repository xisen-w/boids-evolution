"""Stable root adapters for six tabular data services."""
from published.a04_r01 import (
    clean as clean,
    revenue as revenue,
    group as group,
    monthly as monthly,
    lookup as lookup,
    window as window,
)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
