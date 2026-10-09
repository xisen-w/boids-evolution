# Row services

Public API: import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`. Each has signature `(rows, lookup, request)` and returns a new list of dictionaries without mutating its arguments. This package delegates to `published.a07_r03` (dependency declared in `publish.json`).

```python
from candidate import revenue, monthly
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

`clean` normalizes region using strip/lower and fills missing units. Fill modes are `zero`, `mean`, and `median`; an all-missing column fills with zero, and an even-sized median averages its middle values. `revenue` adds `revenue_cents`, null if units or price is null. `group` and `monthly` aggregate non-null revenue, dropping null keys; supported aggregations are sum, mean, count. `lookup` adds the ratio using exact normalized region matching, returning null for unavailable/zero targets or revenue. `window` computes a trailing ROWS mean including the current row. Original row columns and order are retained for row-level services. Dates are expected as ISO strings; numeric fields and request parameters are expected to follow the service specification (fill, agg, window 2/3/4). Invalid parameter values may raise errors.
