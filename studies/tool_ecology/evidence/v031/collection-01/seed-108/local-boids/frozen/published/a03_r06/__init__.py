"""Batch facade over verified row-table transformations."""
from published.a03_r05 import clean, revenue, group, monthly, lookup, window, transform

clean_service = clean
revenue_service = revenue
group_service = group
monthly_service = monthly
lookup_service = lookup
window_service = window

_SERVICES = {
    'clean': clean, 'revenue': revenue, 'group': group,
    'monthly': monthly, 'lookup': lookup, 'window': window,
}

def transform_many(rows, lookup_rows, jobs):
    """Run ordered (family, request) jobs against one unchanged input table.

    Returns a list corresponding to jobs. Each job is a 2-tuple of family
    name and request mapping; family semantics are those of ``transform``.
    """
    results = []
    for family, request in jobs:
        try:
            service = _SERVICES[family]
        except KeyError:
            raise ValueError('unknown service family: %r' % (family,)) from None
        results.append(service(rows, lookup_rows, request))
    return results

__all__ = ['clean','revenue','group','monthly','lookup','window','transform',
           'transform_many','clean_service','revenue_service','group_service',
           'monthly_service','lookup_service','window_service']
