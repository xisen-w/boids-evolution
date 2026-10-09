"""Stable local facade for the six verified tabular service transforms."""
from published.a02_r02 import clean as _clean, revenue as _revenue, group as _group
from published.a02_r02 import monthly as _monthly, lookup as _lookup, window as _window


def clean(rows, lookup, request):
    return _clean(rows, lookup, request)


def revenue(rows, lookup, request):
    return _revenue(rows, lookup, request)


def group(rows, lookup, request):
    return _group(rows, lookup, request)


def monthly(rows, lookup, request):
    return _monthly(rows, lookup, request)


def lookup_service(rows, lookup, request):
    return _lookup(rows, lookup, request)


def window(rows, lookup, request):
    return _window(rows, lookup, request)
