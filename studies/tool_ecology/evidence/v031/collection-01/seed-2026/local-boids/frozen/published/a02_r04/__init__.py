"""Composable dispatcher and stable adapters for tabular services."""
from published.a02_r03 import clean, revenue, group, monthly, window
from published.a02_r03 import lookup_service as lookup

_SERVICES = {
    "clean": clean,
    "revenue": revenue,
    "group": group,
    "monthly": monthly,
    "lookup": lookup,
    "window": window,
}

def run_service(family, rows, lookup_rows, request):
    """Run one service by name; raises ValueError for an unknown family."""
    try:
        function = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError("unknown service family: %r" % (family,))
    return function(rows, lookup_rows, request)
