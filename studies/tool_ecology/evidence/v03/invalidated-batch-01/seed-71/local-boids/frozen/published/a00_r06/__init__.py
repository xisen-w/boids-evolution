"""Composable adapters for recurring row-table transformations."""
from published.a06_r02 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    "clean": clean,
    "revenue": revenue,
    "group": group,
    "monthly": monthly,
    "lookup": lookup,
    "window": window,
}

def transform(family, rows, lookup_rows, request):
    """Run one named service; unknown family names raise KeyError."""
    return _SERVICES[family](rows, lookup_rows, request)

def transform_many(rows, lookup_rows, requests):
    """Run services from {family: request}; returns {family: result}."""
    return {family: transform(family, rows, lookup_rows, request)
            for family, request in requests.items()}
