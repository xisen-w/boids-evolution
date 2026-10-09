"""Native adapters and ordered batch execution for row-table services."""
from published.a06_r02 import clean, revenue, group, monthly, lookup, window

_SERVICES = {"clean": clean, "revenue": revenue, "group": group,
             "monthly": monthly, "lookup": lookup, "window": window}


def transform(family, rows, lookup_rows, request):
    """Execute one named service; unknown service names raise KeyError."""
    return _SERVICES[family](rows, lookup_rows, request)


def transform_many(rows, lookup_rows, requests):
    """Execute mapping of family -> request; retain request iteration order.

    Every service receives the same source rows and lookup table; outputs are
    independent results, not sequentially chained transformations.
    """
    return {name: transform(name, rows, lookup_rows, req)
            for name, req in requests.items()}
