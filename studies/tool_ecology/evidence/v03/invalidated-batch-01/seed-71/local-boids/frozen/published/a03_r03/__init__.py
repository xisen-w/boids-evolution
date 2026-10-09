"""Reusable adapters and bundled analysis for sales row tables."""
from published.a01_r01 import (
    clean as _clean,
    revenue as _revenue,
    group as _group,
    monthly as _monthly,
    lookup as _lookup,
    window as _window,
)


def clean(rows, lookup_rows, request):
    return _clean(rows, lookup_rows, request)


def revenue(rows, lookup_rows, request):
    return _revenue(rows, lookup_rows, request)


def group(rows, lookup_rows, request):
    return _group(rows, lookup_rows, request)


def monthly(rows, lookup_rows, request):
    return _monthly(rows, lookup_rows, request)


def lookup(rows, lookup_rows, request):
    return _lookup(rows, lookup_rows, request)


def window(rows, lookup_rows, request):
    return _window(rows, lookup_rows, request)


def analyze(rows, lookup_rows, request):
    """Return all six service views under stable family-name keys.

    Inputs are passed unchanged to each independent, non-mutating adapter.
    The result is a new dict; each value has the schema of its corresponding
    service. Request must satisfy the union of their parameters.
    """
    return {
        'clean': clean(rows, lookup_rows, request),
        'revenue': revenue(rows, lookup_rows, request),
        'group': group(rows, lookup_rows, request),
        'monthly': monthly(rows, lookup_rows, request),
        'lookup': lookup(rows, lookup_rows, request),
        'window': window(rows, lookup_rows, request),
    }


__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window', 'analyze']
