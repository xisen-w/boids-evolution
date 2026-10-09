# Native table services

Dependency-free Python functions accept `(rows, lookup, request)` and return new lists of dictionaries; inputs are not mutated. Rows and lookup entries follow the service schema. `request.fill` supports `zero`, `mean`, or `median` (even median averages the middle pair; all-missing fills zero). Aggregation uses `request.agg` (`sum`, `mean`, `count`); window uses `request.window` (trailing ROWS, including current).

Public APIs: `clean(rows, lookup, request)` normalizes regions and fills units while retaining columns/order. `revenue(...)` additionally appends `revenue_cents`. `group(...)` returns normalized region groups and `<agg>_revenue_cents`, omitting missing regions. `monthly(...)` groups by YYYY-MM month and normalized region. `lookup(...)` appends `revenue_cents_per_target` using exact normalized region keys; it does not append lookup fields. `window(...)` appends `roll_revenue_cents`.

Example:
```python
from candidate import revenue
rows = [{'units': None, 'price_cents': 25, 'region': ' West '}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```
Unknown targets, zero targets, and missing revenue yield `None`. Group mean for an empty-value group yields `None`; sum/count yield zero. Inputs are expected to be valid schema dictionaries and supported request values.
