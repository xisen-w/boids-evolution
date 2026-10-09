"""Row-table service adapters and family dispatcher."""
from published.a01_r01 import clean as _clean, revenue as _revenue
from published.a01_r01 import group as _group, monthly as _monthly
from published.a01_r01 import lookup as _lookup, window as _window


def clean(rows, lookup, request):
    return _clean(rows, lookup, request)


def revenue(rows, lookup, request):
    return _revenue(rows, lookup, request)


def group(rows, lookup, request):
    return _group(rows, lookup, request)


def monthly(rows, lookup, request):
    return _monthly(rows, lookup, request)


def lookup(rows, lookup_rows, request):
    return _lookup(rows, lookup_rows, request)


def window(rows, lookup, request):
    return _window(rows, lookup, request)


_SERVICES = {name: globals()[name] for name in
             ('clean', 'revenue', 'group', 'monthly', 'lookup', 'window')}


def run(family, rows, lookup_rows, request):
    """Run a named family; raise ValueError for an unknown family."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError(f"unknown family: {family!r}") from None
    return service(rows, lookup_rows, request)


__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window', 'run']
