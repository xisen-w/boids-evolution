"""Composable regional-sales row services."""
from published.a06_r04 import clean, revenue, group, monthly, lookup, window
from published.a06_r04 import transform as _dispatch

_SERVICES = {
    'clean': clean, 'revenue': revenue, 'group': group,
    'monthly': monthly, 'lookup': lookup, 'window': window,
}

def transform(family, rows, lookup_rows, request):
    """Dispatch one exact service family; unknown names raise KeyError."""
    return _dispatch(family, rows, lookup_rows, request)

def transform_many(rows, lookup_rows, requests):
    """Execute named family requests against shared input tables.

    `requests` maps family names to requests. Returns an insertion-ordered dict
    mapping those names to full outputs. Inputs are not modified; each service
    receives the same original tables. Unknown names raise KeyError.
    """
    return {name: _SERVICES[name](rows, lookup_rows, req)
            for name, req in requests.items()}
