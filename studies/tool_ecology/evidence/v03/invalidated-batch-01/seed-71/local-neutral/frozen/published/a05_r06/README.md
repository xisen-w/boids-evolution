# Row-table services

Pure native-Python transformations for the six row-table service families. Every public adapter accepts `(rows, lookup, request)` and returns fresh dictionaries; inputs are not mutated.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' West ', 'date': '2025-03-01', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' West ', 'date': '2025-03-01', 'units': 2,
#   'price_cents': 50, 'revenue_cents': 100}]
```

`clean` normalizes region and fills units. `revenue` fills units and adds `revenue_cents`. `group` and `monthly` aggregate nonmissing revenue by normalized nonmissing group keys. `lookup` adds `revenue_cents_per_target`, matching normalized region keys from lookup rows, without adding lookup fields. `window` adds the mean of nonmissing revenue over trailing ROWS including current.

Request keys: `fill` is `zero`, `mean`, or `median` (all missing -> 0; even median averages the middle pair); grouped `agg` is `sum`, `mean`, or `count` (count ignores missing revenue); `window` is width 2, 3, or 4. Empty sum/count aggregates are 0 and empty means are None. Group results sort lexically. Missing values are represented by `None`. Inputs are expected to follow the specified schema and valid request values.
