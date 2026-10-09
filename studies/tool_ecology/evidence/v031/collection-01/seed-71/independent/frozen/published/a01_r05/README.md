# Tabular service adapters

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`. Each public function (and corresponding `*_check` alias) accepts `(rows, lookup, request)` and returns a new list of dictionaries; input objects are not mutated. This package re-exports the service-verified implementation from `published.a01_r04` (which depends on `a01_r02`).

```python
from candidate import revenue, monthly
rows = [{'region': ' North ', 'units': None, 'price_cents': 5}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
monthly(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [] -- rows without a date are excluded from monthly groups
```

`clean` strips and lowercases region and fills missing units by `zero`, `mean`, or `median` (all-missing fills with zero; even median averages the middle pair). `revenue` adds `revenue_cents`, `None` when units or price is missing. `group` and `monthly` normalize region, discard missing group keys, and aggregate nonmissing revenue with `sum`, `mean`, or `count`; monthly also uses the first seven date characters. `lookup` adds `revenue_cents_per_target` using exact normalized region lookup; missing/unknown/zero targets and missing revenue produce `None`. `window` adds the mean of nonmissing revenues among trailing `request.window` rows, including current (allowed sizes 2, 3, 4). Row transformations preserve original column values/order and row order; grouped results are sorted by stringified keys. Invalid modes/sizes raise `ValueError`; dates are expected as ISO strings.
