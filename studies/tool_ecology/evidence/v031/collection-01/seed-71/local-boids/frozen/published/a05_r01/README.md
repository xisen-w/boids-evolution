# Row services

Native, dependency-free Python functions accept `(rows, lookup, request)` and return new lists of dictionaries; inputs are not mutated. Public APIs are `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)` (also exported from the package root).

```python
from candidate import group, window
rows = [{'region': ' West ', 'date': '2025-01-02', 'units': 2,
         'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
assert window(rows, [], {'fill': 'zero', 'window': 2})[0]['roll_revenue_cents'] == 100
```

All services normalize string regions by stripping and lowercasing. Missing units are filled by `request['fill']` (`zero`, `mean`, or `median`; default `zero`), with all-missing values filled with zero. Revenue and downstream services append/derive `revenue_cents`; missing operands produce `None`. `group` aggregates by region and `monthly` by YYYY-MM month and region, using `request['agg']` (`sum`, `mean`, `count`; default `sum`). Groups omit missing keys; means with no nonmissing revenue are `None`. `lookup` appends `revenue_cents_per_target`, matching normalized region keys and yielding `None` for absent/zero targets or missing revenue. `window` appends the trailing-row mean in `roll_revenue_cents`, using `request['window']` (default 2); missing revenues do not contribute, but rows still occupy window positions. Unsupported parameters raise `ValueError`. Lookup duplicate normalized keys resolve to the last row. No schema validation beyond these parameter checks is performed.
