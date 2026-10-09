"""Compatibility-stable entry points for sales row transformations."""
from published.a05_r01 import clean as _clean
from published.a05_r01 import revenue as _revenue
from published.a05_r01 import group as _group
from published.a05_r01 import monthly as _monthly
from published.a05_r01 import lookup as _lookup
from published.a05_r01 import window as _window


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
