"""Streaming and named dispatch for standard tabular services."""
from published.a07_r02 import clean, revenue, group, monthly, lookup as lookup_service, window

_SERVICES = {
    "clean": clean,
    "revenue": revenue,
    "group": group,
    "monthly": monthly,
    "lookup": lookup_service,
    "window": window,
}

def process(family, rows, lookup, request):
    """Run a named family service; unknown family names raise ValueError."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError(f"unknown service family: {family!r}") from None
    return service(rows, lookup, request)

def process_many(jobs):
    """Run four-item (family, rows, lookup, request) jobs, in order."""
    return [process(*job) for job in jobs]

def process_iter(jobs):
    """Lazily process jobs; each is (family, rows, lookup, request).

    A job is evaluated only when requested from the returned iterator. Exceptions
    propagate at that point; subsequent jobs are not attempted automatically.
    """
    for job in jobs:
        yield process(*job)

def clean_adapter(rows, lookup, request): return process("clean", rows, lookup, request)
def revenue_adapter(rows, lookup, request): return process("revenue", rows, lookup, request)
def group_adapter(rows, lookup, request): return process("group", rows, lookup, request)
def monthly_adapter(rows, lookup, request): return process("monthly", rows, lookup, request)
def lookup_adapter(rows, lookup, request): return process("lookup", rows, lookup, request)
def window_adapter(rows, lookup, request): return process("window", rows, lookup, request)
