"""Sales table transformations; adapters accept rows, lookup, request."""
from published.a05_r01 import clean, revenue, group, monthly, window
from published.a05_r01 import lookup as _lookup


def lookup_service(rows, lookup, request):
    """Normalize, derive revenue, and append revenue per region target."""
    return _lookup(rows, lookup, request)
