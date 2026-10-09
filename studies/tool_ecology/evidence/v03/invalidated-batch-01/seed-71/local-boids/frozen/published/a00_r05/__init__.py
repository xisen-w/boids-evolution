"""Composable, non-mutating adapters for regional sales table services."""
from published.a06_r04 import clean, revenue, group, monthly, lookup, window
from published.a06_r04 import transform as _transform

_SERVICES = {
    "clean": clean, "revenue": revenue, "group": group,
    "monthly": monthly, "lookup": lookup, "window": window,
}

def transform(family, rows, lookup_rows, request):
    """Run one family by exact name; unknown names raise KeyError."""
    return _transform(family, rows, lookup_rows, request)

def transform_many(rows, lookup_rows, requests):
    """Run family-specific requests, returning {family: full service output}.

    Each request is independently passed to its adapter; inputs are not mutated.
    Empty requests produce {} and unknown family names raise KeyError.
    """
    return {family: _SERVICES[family](rows, lookup_rows, req)
            for family, req in requests.items()}
