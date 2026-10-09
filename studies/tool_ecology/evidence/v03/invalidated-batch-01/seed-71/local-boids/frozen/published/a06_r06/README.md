# Row-table service adapters

Exports `clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`,
`monthly(...)`, `lookup(...)`, and `window(...)`. These return the complete
service-specific tables according to the recurring row-table contract. Fill
options are zero/mean/median; aggregations are sum/mean/count; window is a
trailing number of rows including the current row.

`transform(family, rows, lookup_rows, request)` calls one adapter and raises
`KeyError` for an unknown family. `transform_many(rows, lookup_rows, requests)`
accepts an insertion-ordered mapping from family name to its request and
returns a mapping of results in that order. Each operation uses the original
input rows (results are not chained); input mutation/validation behavior follows
the underlying service implementation.

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
