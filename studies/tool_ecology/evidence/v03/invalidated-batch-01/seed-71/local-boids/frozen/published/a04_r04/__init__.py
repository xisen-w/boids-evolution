"""Row-table service facade with a family dispatcher."""
from published.a06_r03 import transform as _transform

def transform(family, rows, lookup, request):
    """Dispatch one of the six services; unknown family raises KeyError."""
    return _transform(family, rows, lookup, request)

def clean(rows, lookup, request):
    return transform('clean', rows, lookup, request)

def revenue(rows, lookup, request):
    return transform('revenue', rows, lookup, request)

def group(rows, lookup, request):
    return transform('group', rows, lookup, request)

def monthly(rows, lookup, request):
    return transform('monthly', rows, lookup, request)

def lookup_service(rows, lookup, request):
    return transform('lookup', rows, lookup, request)

def window(rows, lookup, request):
    return transform('window', rows, lookup, request)

# Keep the service's required public name while avoiding parameter shadowing confusion.
lookup = lookup_service
__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window', 'transform']
