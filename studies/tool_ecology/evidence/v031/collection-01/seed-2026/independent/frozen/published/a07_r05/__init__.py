"""Stable public namespace for the verified native table-service toolkit."""
from published.a07_r04 import clean, revenue, group, monthly, lookup as lookup_service, window

# Service check adapters: each accepts (rows, lookup, request).
def lookup(rows, lookup, request):
    return lookup_service(rows, lookup, request)
