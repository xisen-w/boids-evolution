# Candidate table services

This package provides a stable Python namespace for the six row-oriented table services, delegating to the verified native implementation in `published.a07_r04` (declared dependency). Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`; each has signature `(rows, lookup, request)` and returns newly constructed output without mutating inputs.

Example:

```python
from candidate import revenue, group
rows = [dict(id=1, region=' West ', product='x', date='2024-03-10', units=None, price_cents=20, cost_cents=2)]
request = {'fill': 'zero', 'agg': 'sum'}
assert revenue(rows, [], request)[0]['revenue_cents'] == 0
assert group(rows, [], request) == [{'region': 'west', 'sum_revenue_cents': 0}]
```

Fill options are `zero`, `mean`, and `median`; grouping aggregation options are `sum`, `mean`, and `count`; rolling windows accept 2, 3, or 4 rows. Region normalization, missing-value behavior, output ordering, and aggregation semantics follow the dependency's documented API. Inputs are lists of dictionaries and request options must be supplied as documented. No extra third-party packages are required beyond the declared package dependency.
