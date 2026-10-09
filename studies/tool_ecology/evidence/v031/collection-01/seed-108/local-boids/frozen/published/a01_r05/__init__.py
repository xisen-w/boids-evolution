"""Row-table service adapters and batch dispatch."""
from published.a03_r02 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    'clean': clean, 'revenue': revenue, 'group': group,
    'monthly': monthly, 'lookup': lookup, 'window': window,
}

def run(family, rows, lookup_rows, request):
    """Run one supported service, rejecting unknown family names."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError('unknown service family: %r' % (family,)) from None
    return service(rows, lookup_rows, request)

def run_many(families, rows, lookup_rows, request):
    """Return {family: result} for each requested family, without mutating inputs.

    Each invocation receives the same input objects; service implementations are
    expected not to mutate them. Duplicate family names collapse in the result.
    """
    return {family: run(family, rows, lookup_rows, request) for family in families}

clean_service = clean
revenue_service = revenue
group_service = group
monthly_service = monthly
lookup_service = lookup
window_service = window
__all__ = ['clean','revenue','group','monthly','lookup','window','run','run_many',
           'clean_service','revenue_service','group_service','monthly_service','lookup_service','window_service']
