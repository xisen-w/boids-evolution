# Row-table transformations

This package provides the six recurring services through the stable APIs
`clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`,
`monthly(...)`, `lookup(...)`, and `window(...)`. Their behavior follows the
service contract: fill is zero/mean/median; aggregation is sum/mean/count;
window is a trailing ROWS window. Results are fresh output, preserving source
row order for row-wise services. Implementations are reused from the verified
`published.a06_r02` package; malformed input behavior follows that dependency.

`transform(family, rows, lookup_rows, request)` dispatches one service and
raises `KeyError` for an unsupported family. `transform_many(rows, lookup_rows,
requests)` takes a mapping from service name to its request, runs each against
the same inputs, and returns a mapping in request iteration order.

```python
from candidate import transform_many
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
result = transform_many(rows, [], {
    'revenue': {'fill': 'zero'},
    'group': {'fill': 'zero', 'agg': 'sum'},
})
assert result['revenue'][0]['revenue_cents'] == 100
assert result['group'] == [{'region': 'west', 'sum_revenue_cents': 100}]
```
