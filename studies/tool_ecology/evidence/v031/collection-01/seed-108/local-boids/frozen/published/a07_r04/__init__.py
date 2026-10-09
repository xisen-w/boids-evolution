"""Row-table service adapters and a family-selecting dispatcher."""
from published.a03_r02 import clean, revenue, group, monthly, lookup, window

_SERVICES = {
    'clean': clean, 'revenue': revenue, 'group': group,
    'monthly': monthly, 'lookup': lookup, 'window': window,
}

def run(family, rows, lookup_rows, request):
    """Run one named service; family is one of clean/revenue/group/monthly/lookup/window."""
    try:
        service = _SERVICES[family]
    except (KeyError, TypeError):
        raise ValueError('unknown service family: %r' % (family,)) from None
    return service(rows, lookup_rows, request)

clean_service = clean
revenue_service = revenue
group_service = group
monthly_service = monthly
lookup_service = lookup
window_service = window
__all__ = ['clean','revenue','group','monthly','lookup','window','run','clean_service','revenue_service','group_service','monthly_service','lookup_service','window_service']
