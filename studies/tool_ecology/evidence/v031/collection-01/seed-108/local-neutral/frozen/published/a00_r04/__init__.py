"""Row-table services, reusing the verified a00_r02 implementation."""
from published import a00_r02 as _base


def clean(rows, lookup, request):
    return _base.clean(rows, lookup, request)


def revenue(rows, lookup, request):
    return _base.revenue(rows, lookup, request)


def group(rows, lookup, request):
    return _base.group(rows, lookup, request)


def monthly(rows, lookup, request):
    return _base.monthly(rows, lookup, request)


def lookup_service(rows, lookup, request):
    return _base.lookup(rows, lookup, request)


def window(rows, lookup, request):
    return _base.window(rows, lookup, request)

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup_service', 'window']
