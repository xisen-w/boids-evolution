# Tabular service adapters

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`. Every API is `function(rows, lookup_rows, request)` and returns fresh dictionaries/lists without mutating inputs. This package delegates to the received, verified `published.a01_r03` implementation; it has no additional runtime requirements.

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' West ', 'units': 0, 'price_cents': 25, 'revenue_cents': 0}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'west', 'sum_revenue_cents': 0}]
```

`clean` normalizes region by strip/lower and fills missing units. `revenue` fills units and appends revenue (region remains as supplied). `group` and `monthly` normalize region, derive revenue, drop missing grouping keys and aggregate nonmissing revenue. `monthly` groups by the first seven date characters. `lookup` normalizes region, derives revenue and appends revenue per exact normalized region target; target/manager are not added. `window` appends the mean over trailing physical rows including current. All preserve existing column order and append derived fields. Fill modes are `zero`, `mean`, `median`; all-missing units fill with zero and even median averages central values. Aggregations are `sum`, `mean`, `count`; count counts nonmissing revenues. Empty aggregates return zero for sum/count and `None` for mean. Unknown regions, missing values, and zero targets yield `None` for per-target revenue where applicable. Windows accepted are 2, 3, and 4. Invalid modes raise `ValueError`.
