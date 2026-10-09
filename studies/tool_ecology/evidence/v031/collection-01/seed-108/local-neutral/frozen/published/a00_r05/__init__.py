"""Row-table transformation services with non-mutating functional APIs."""
from published import a00_r04 as _services

clean = _services.clean
revenue = _services.revenue
group = _services.group
monthly = _services.monthly
lookup_service = _services.lookup_service
window = _services.window

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup_service', 'window']
