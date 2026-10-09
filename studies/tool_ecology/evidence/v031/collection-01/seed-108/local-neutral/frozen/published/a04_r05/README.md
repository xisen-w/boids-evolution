# Tabular services

The package exports `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts
row dictionaries, a lookup-row list, and a request dictionary and returns a new
list of dictionaries without mutating inputs.

`clean` normalizes non-null regions (strip/lower) and fills null units.
`revenue` fills units and appends `revenue_cents`; missing operands produce None.
`group` groups non-null normalized regions and aggregates nonmissing revenues.
`monthly` groups by month and normalized region, dropping missing keys.
`lookup` adds `revenue_cents_per_target` by exact normalized region; missing or
zero targets and missing revenue produce None. `window` adds the trailing ROWS
mean `roll_revenue_cents`, including the current row.

`request.fill` is `zero`, `mean`, or `median`; all-null inputs fill with zero
and an even median averages the central pair. `request.agg` is `sum`, `mean`, or
`count`. `request.window` is 2, 3, or 4. Example:

```python
from candidate import revenue
revenue([{"units": None, "price_cents": 5}], [], {"fill": "zero"})
# [{'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```

Invalid parameter values may raise `ValueError`. Implementation is delegated
to the received, verified `published.a02_r03` package; that package is a required
dependency. Inputs are expected to use the documented row schemas.
