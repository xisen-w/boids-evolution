# Native tabular services

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. All functions accept a list of row mappings, a lookup-row list, and a request mapping; return fresh dictionaries and do not mutate inputs.

`clean` normalizes region using strip/lower and fills missing units. `revenue` fills units and adds `revenue_cents` without changing region. `group` and `monthly` normalize region, derive revenue and aggregate nonmissing revenue by region or month/region. `lookup` normalizes row and lookup regions and adds `revenue_cents_per_target`. `window` derives revenue without region normalization and adds the trailing-row mean `roll_revenue_cents`.

Fill mode is `request['fill']` (`zero`, `mean`, or `median`), default `zero`; all-missing units fill with zero. Aggregation is `request['agg']` (`sum`, `mean`, or `count`), default `sum`; empty means are `None`. Window size is `request['window']` (2, 3, or 4), default 2. Invalid options raise `ValueError`; inputs are expected to follow the documented service schema. Duplicate normalized lookup keys use the last lookup row.

Example:
```python
from candidate import group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'agg': 'sum'}) == [
    {'region': 'north', 'sum_revenue_cents': 100}
]
```
