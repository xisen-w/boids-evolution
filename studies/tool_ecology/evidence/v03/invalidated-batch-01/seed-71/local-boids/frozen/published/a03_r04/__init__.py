"""Reusable adapters for the six sales-table service families."""
from published.a01_r01 import clean, revenue, group, monthly, lookup, window


def analyze(rows, lookup_rows, request):
    """Return all six views as a dict keyed by family name."""
    return {
        'clean': clean(rows, lookup_rows, request),
        'revenue': revenue(rows, lookup_rows, request),
        'group': group(rows, lookup_rows, request),
        'monthly': monthly(rows, lookup_rows, request),
        'lookup': lookup(rows, lookup_rows, request),
        'window': window(rows, lookup_rows, request),
    }
