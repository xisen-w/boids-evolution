"""Stable concise facade for the verified row-table service implementations."""
from published.a00_r01 import clean as _clean, revenue as _revenue
from published.a00_r01 import group as _group, monthly as _monthly
from published.a00_r01 import lookup as _lookup, window as _window


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
