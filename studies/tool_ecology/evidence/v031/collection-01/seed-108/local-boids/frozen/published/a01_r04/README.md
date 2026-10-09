# Row-table service adapters

This package provides six pure-Python adapters. Each public callable accepts
`(rows, lookup, request)` and returns a fresh list of dictionaries without
mutating the supplied data. Example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' West ', 'units': 0, 'price_cents': 25, 'revenue_cents': 0}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'west', 'sum_revenue_cents': 0}]
```

APIs: `clean(rows, lookup, request)` normalizes region via strip/lower and fills
missing units; `revenue(...)` fills units and appends `revenue_cents` without
normalizing region; `group(...)` aggregates revenue by normalized region;
`monthly(...)` aggregates by YYYY-MM and normalized region; `lookup(...)` appends
`revenue_cents_per_target` using exact normalized region matching; `window(...)`
appends the trailing-row mean `roll_revenue_cents` (including current row).
Lookup data consists of dictionaries with `region`, `target`, and `manager`;
manager is not returned. Request fields are `fill` (`zero`, `mean`, `median`),
`agg` (`sum`, `mean`, `count`), and `window` (row width). Missing units are
filled from nonmissing values (even median averages the middle pair; all-missing
fills with zero). Missing revenue is excluded from aggregation and window means;
empty sum/count are zero and empty mean is `None`. Null grouping keys are omitted.
Unknown/zero/null targets and null revenue produce null per-target revenue.

Inputs and request choices are expected to follow the service schema and valid
option values; this adapter delegates semantics to `published.a06_r02`.
