# Row service toolkit

A dependency-backed native Python interface to the six row-table services. The public adapters are `clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)`. `lookup` is the service function name; its second argument is the lookup table. All return fresh result data and do not mutate inputs.

`run(family, rows, lookup_rows, request)` dispatches to an adapter using one of `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`; unknown names raise `ValueError`.

Example:
```python
from candidate import run
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert run('group', rows, [], {'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}
]
```

Fill mode is `request.fill` (`zero`, `mean`, or `median`; all-missing units fill as zero). Group aggregations use `request.agg` (`sum`, `mean`, `count`); windows use `request.window` (2, 3, or 4). Region normalization and missing-value, ordering, and aggregation semantics follow the service contract. This package delegates implementations to `published.a00_r02`, which is declared as a dependency. Inputs are expected to conform to the documented row/request schema; malformed inputs are not validated.
