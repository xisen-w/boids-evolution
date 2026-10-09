"""Convenient facade for six tested tabular row services."""
from published.a04_r03 import clean, revenue, group, monthly, lookup_service, window

def serve_clean(rows, lookup, request): return clean(rows, lookup, request)
def serve_revenue(rows, lookup, request): return revenue(rows, lookup, request)
def serve_group(rows, lookup, request): return group(rows, lookup, request)
def serve_monthly(rows, lookup, request): return monthly(rows, lookup, request)
def serve_lookup(rows, lookup, request): return lookup_service(rows, lookup, request)
def serve_window(rows, lookup, request): return window(rows, lookup, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup_service', 'window',
           'serve_clean', 'serve_revenue', 'serve_group', 'serve_monthly', 'serve_lookup', 'serve_window']
