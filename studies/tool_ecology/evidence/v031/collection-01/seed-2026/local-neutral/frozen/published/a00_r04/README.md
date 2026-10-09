# Sales table service adapters

This package re-exports the verified native-Python adapters from
`published.a00_r03`, providing a compact stable import surface. Every adapter
accepts `(rows, lookup, request)` and returns fresh results without mutating
its inputs.

- `clean`: normalize region via strip/lower and fill missing units.
- `revenue`: clean behavior plus `revenue_cents`.
- `group`: aggregate nonmissing revenue by normalized region.
- `monthly`: aggregate by month and normalized region.
- `lookup`: add `revenue_cents_per_target` from exact region lookup.
- `window`: add trailing row-window mean `roll_revenue_cents`.

`request.fill` supports `zero`, `mean`, and `median` (even medians average
central values; all-missing fills with zero). `request.agg` supports `sum`,
`mean`, `count`; empty sum/count are zero and empty mean is `None`.
`request.window` specifies the trailing row count. Aggregations drop missing
keys and sort by stringified keys. Expected inputs follow the service contract.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```
