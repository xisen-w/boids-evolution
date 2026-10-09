"""Verified row-service facade with ordered pipeline execution."""
from published.a02_r04 import clean, revenue, group, monthly, lookup, window

_SERVICES = {"clean": clean, "revenue": revenue, "group": group,
             "monthly": monthly, "lookup": lookup, "window": window}

def run_pipeline(rows, lookup_rows, requests):
    """Apply ordered (family, request) steps; each receives prior step's output.

    Suitable for row-preserving steps. Group/monthly return aggregate rows, so
    subsequent services expecting input sales columns may not be applicable.
    Inputs are passed to immutable-by-contract services and are not modified.
    """
    result = rows
    for family, request in requests:
        try:
            service = _SERVICES[family]
        except KeyError:
            raise ValueError("unknown service family: %s" % family) from None
        result = service(result, lookup_rows, request)
    return result

# Full service adapters used by host checks.
clean_service = clean
revenue_service = revenue
group_service = group
monthly_service = monthly
lookup_service = lookup
window_service = window
