"""Compositional row-table service adapters."""
from published.a06_r03 import clean, revenue, group, monthly, lookup, window
from published.a06_r03 import transform as _transform

_SERVICES = {name: fn for name, fn in {
    "clean": clean, "revenue": revenue, "group": group,
    "monthly": monthly, "lookup": lookup, "window": window,
}.items()}

def transform(family, rows, lookup_rows, request):
    """Run one service by exact family name."""
    return _transform(family, rows, lookup_rows, request)

def transform_many(rows, lookup_rows, requests):
    """Run multiple services over the same inputs.

    requests maps exact family names to request dictionaries. Returns a dict
    with matching keys and each family's full result. Input objects are passed
    through to nonmutating services; no result is merged with another.
    Unknown families raise KeyError. Empty mapping returns an empty dict.
    """
    return {family: _SERVICES[family](rows, lookup_rows, request)
            for family, request in requests.items()}
