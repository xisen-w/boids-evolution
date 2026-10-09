# Verified tabular service adapters

This package exposes six non-mutating `(rows, lookup, request)` adapters and delegates their implementation to the received, service-verified `published.a01_r02` package. Each returns newly allocated dictionaries; inputs are not modified.

```python
from candidate import revenue, monthly
rows = [{'region': ' North ', 'units': None, 'price_cents': 5}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```

`clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` are also exposed as `*_check` names for service harnesses. Fill modes are `zero`, `mean`, and `median` (all-missing units become zero; even medians average the middle values). Clean normalizes region; revenue and window preserve it, while group/monthly/lookup normalize it. Aggregations are `sum`, `mean`, or `count`; missing revenues are ignored. Monthly groups by the first seven date characters. Lookup adds only revenue per target. Window computes a trailing-row mean including the current row. See the `a01_r02` implementation documentation for full edge behavior; unsupported modes raise `ValueError`.
