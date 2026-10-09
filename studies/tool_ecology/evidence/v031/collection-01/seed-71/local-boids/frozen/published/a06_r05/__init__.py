"""Pure row services plus ordered multi-family execution."""
from published.a06_r04 import clean, revenue, group, monthly, lookup, window, run_service

SERVICES = {"clean": clean, "revenue": revenue, "group": group,
            "monthly": monthly, "lookup": lookup, "window": window}

def run_services(families, rows, lookup_rows, request):
    """Run requested family names in order; return {family: result}.

    Duplicate names are evaluated in order and the final result for that key is
    retained. Unknown names raise KeyError. Inputs are passed unchanged to pure
    service adapters.
    """
    result = {}
    for family in families:
        result[family] = run_service(family, rows, lookup_rows, request)
    return result

__all__ = ["clean", "revenue", "group", "monthly", "lookup", "window", "run_service", "run_services"]
