# tabular services

This dependency-free package exposes six public functions. Each takes
`(rows, lookup, request)` and returns new dictionaries/lists; inputs are not
mutated. `rows` is a list of row dictionaries, `lookup` a list of dictionaries,
and `request` a dictionary.

* `clean(rows, lookup, request)`: strip/lower string regions and fill missing
  `units`; otherwise retain columns and row order.
* `revenue(rows, lookup, request)`: same fill/normalization, append
  `revenue_cents` (`units * price_cents`, or `None` if either is missing).
* `group(rows, lookup, request)`: aggregate nonmissing revenue by nonmissing
  region, returning `region` and `<agg>_revenue_cents`.
* `monthly(rows, lookup, request)`: aggregate by nonmissing month (`date[:7]`)
  and region, returning `month`, `region`, and `<agg>_revenue_cents`.
* `lookup_service(rows, lookup, request)`: revenue output plus
  `revenue_cents_per_target`; lookup regions are strip/lower normalized.
* `window(rows, lookup, request)`: revenue output plus mean of nonmissing
  revenue in the trailing positional `window` rows, including the current row.

`request.fill` is `zero`, `mean`, or `median` (default `zero`); an all-missing
units column is filled with zero. `request.agg` is `sum`, `mean`, or `count`
(default `sum`). Empty sum/count groups evaluate to zero and empty means to
`None`. `request.window` is 2, 3, or 4. Group results are sorted by stringified
keys. Lookup returns `None` for missing revenue, unknown region, missing target,
or zero target. Extra input columns are retained by row-oriented services;
aggregate services return only their documented columns.

Example:

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': None, 'price_cents': 5}]
request = {'fill': 'zero', 'agg': 'sum'}
assert revenue(rows, [], request)[0]['revenue_cents'] == 0
assert group(rows, [], request) == [
    {'region': 'north', 'sum_revenue_cents': 0}
]
```

Adapters `serve_clean`, `serve_revenue`, `serve_group`, `serve_monthly`,
`serve_lookup`, and `serve_window` have the same three-argument signature and
are the publication service entry points. Inputs are expected to follow the
specified service schema and valid request choices; malformed schemas are not
coerced.
