# Row-table services

Imports native, verified implementations from `published.a06_r02` and exposes
six adapters: `clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`,
`monthly(...)`, `lookup(...)`, and `window(...)`. Each returns the complete
output for that service family; service semantics and request options are those
of the corresponding recurring service contract (fill: zero/mean/median;
aggregation: sum/mean/count; window: 2/3/4).

`transform(family, rows, lookup_rows, request)` invokes one adapter and raises
`KeyError` for an unknown family. `transform_many(rows, lookup_rows, requests)`
accepts a mapping from family name to that family's request and returns a
mapping of family to complete output, retaining mapping iteration order.

```python
from candidate import transform_many
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
out = transform_many(rows, [], {
    'revenue': {'fill': 'zero'},
    'group': {'fill': 'zero', 'agg': 'sum'},
})
assert out['revenue'][0]['revenue_cents'] == 100
assert out['group'] == [{'region': 'west', 'sum_revenue_cents': 100}]
```

No additional validation or schema conversion is performed; malformed input
behavior follows the underlying implementations. Dispatch itself does not
mutate inputs.
