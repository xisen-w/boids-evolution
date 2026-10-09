"""Six tested, non-mutating tabular service functions (implemented in a dependency)."""
from published.a04_r03 import (
    clean, revenue, group, monthly, lookup_service, window,
    serve_clean, serve_revenue, serve_group, serve_monthly, serve_lookup, serve_window,
)
__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup_service', 'window',
           'serve_clean', 'serve_revenue', 'serve_group', 'serve_monthly', 'serve_lookup', 'serve_window']
