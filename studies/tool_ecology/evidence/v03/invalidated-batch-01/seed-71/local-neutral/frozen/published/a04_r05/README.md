# Row-table service API

This package exposes six pure service adapters. Import with `from candidate import clean, revenue, group, monthly, lookup, window`; each callable accepts `(rows, lookup, request)` and returns fresh dictionaries without mutating its inputs. Example:

```python
from candidate import monthly
monthly([{'region':' West ', 'date':'2025-03-12', 'units':2, 'price_cents':50}], [], {'fill':'mean', 'agg':'sum'})
# [{'month': '2025-03', 'region': 'west', 'sum_revenue_cents': 100}]
```

`clean` normalizes region and fills missing units; `revenue` fills units and derives revenue; `group`/`monthly` aggregate nonmissing revenue (sum, mean, count); `lookup` adds per-target revenue; `window` adds trailing-row revenue mean. Fill options are zero/mean/median (all missing becomes zero); aggregation options are sum/mean/count. Row outputs retain columns and order. See the service contract for null-key dropping and missing-value rules. Inputs and options are expected to follow the specified schema and valid values. This package delegates to the received, independently service-verified `published.a04_r04` implementation.
