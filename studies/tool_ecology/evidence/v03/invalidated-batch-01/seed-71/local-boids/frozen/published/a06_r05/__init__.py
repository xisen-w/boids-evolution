"""Row-table service facade and deterministic multi-service dispatcher."""
from published.a06_r02 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    "clean": clean, "revenue": revenue, "group": group,
    "monthly": monthly, "lookup": lookup, "window": window,
}


def transform(family, rows, lookup_rows, request):
    """Run one family, raising KeyError if family is unsupported."""
    return _SERVICES[family](rows, lookup_rows, request)


def transform_many(rows, lookup_rows, requests):
    """Run each named family request; return results in request iteration order.

    ``requests`` maps family names to request dictionaries. Inputs are passed
    through unchanged and are not modified by this dispatcher.
    """
    return {family: transform(family, rows, lookup_rows, request)
            for family, request in requests.items()}
