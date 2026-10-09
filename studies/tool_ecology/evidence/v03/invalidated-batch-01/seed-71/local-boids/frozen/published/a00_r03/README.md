# Row service adapters

This package exposes pure service functions `clean(rows, lookup, request)`,
`revenue(rows, lookup, request)`, `group(rows, lookup, request)`,
`monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and
`window(rows, lookup, request)`. It re-exports the verified implementations
from `published.a00_r02` (shipped dependency). Inputs are lists of row
mappings, lookup is a sequence of `{region, target, manager}` mappings, and
request is a mapping.

`clean` normalizes region by stripping and lowercasing and fills missing units
according to `request.fill` (`zero`, `mean`, `median`; all missing fills zero).
`revenue` adds `revenue_cents`. `group` and `monthly` aggregate nonmissing
revenue using `request.agg` (`sum`, `mean`, `count`); monthly groups by the
first seven date characters. `lookup` adds `revenue_cents_per_target` using
exact normalized region keys. `window` adds trailing ROWS mean in
`roll_revenue_cents`, with width `request.window` (2, 3, or 4). Functions
return fresh outputs and do not mutate input data.

Example:
```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}
]
```

The API expects the documented row schema and valid request choices; it is
not a general-purpose schema validator.
