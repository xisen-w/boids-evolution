# Tabular row services

This package exposes six pure row-list adapters, with signature `(rows, lookup, request)`: `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`. It delegates to the received, service-verified `published.a04_r05` implementation and declares that package as its sole dependency.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'id': 1, 'region': ' West ', 'units': None,
         'price_cents': 200, 'date': '2025-03-02'}]
cleaned = clean(rows, [], {'fill': 'zero'})
assert cleaned[0]['region'] == 'west' and cleaned[0]['units'] == 0
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 0}]
```

Inputs are not mutated. See the common service contract for fill modes (`zero`, `mean`, `median`), aggregations (`sum`, `mean`, `count`), and window widths (2, 3, 4). Row adapters preserve columns and order; group/monthly return aggregated rows. No external runtime dependency is introduced. Invalid parameter values follow the delegated implementation's `ValueError` behavior.
