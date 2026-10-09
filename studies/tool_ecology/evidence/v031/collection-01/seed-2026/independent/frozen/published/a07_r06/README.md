# Row-table services

Native Python service adapters accepting `(rows, lookup, request)` and returning new output without mutating inputs. Public callables are `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.

```python
from candidate import revenue, group
rows = [dict(id=1, region=' West ', product='x', date='2024-03-10', units=None, price_cents=20, cost_cents=2)]
req = {'fill': 'zero', 'agg': 'sum'}
assert revenue(rows, [], req)[0]['revenue_cents'] == 0
assert group(rows, [], req) == [{'region': 'west', 'sum_revenue_cents': 0}]
```

`clean` strips/lowercases region and fills missing units (zero, mean, median; all-missing becomes zero), retaining columns/order. `revenue` adds `revenue_cents`, null when an operand is missing. Group and monthly aggregate nonmissing revenue and drop missing grouping keys; monthly derives the first seven date characters. `lookup` adds per-target revenue for exact normalized region matches (unknown/missing/zero target gives null). `window` adds the trailing row-window mean of available revenue. Aggregations are sum/mean/count; rolling widths are 2, 3, or 4. Grouped output is sorted as specified by the service contract. Requires the declared `published.a07_r05` dependency; no third-party dependencies.
