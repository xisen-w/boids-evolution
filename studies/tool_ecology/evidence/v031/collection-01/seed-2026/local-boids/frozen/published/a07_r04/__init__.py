"""Six non-mutating table services, delegated to the verified a07_r03 package."""
from published.a07_r03 import clean, revenue, group, monthly, window
from published.a07_r03 import lookup_service as lookup

__all__ = ['clean', 'revenue', 'group', 'monthly', 'lookup', 'window']
