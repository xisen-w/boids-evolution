# Tabular service adapters

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` (also available as corresponding `*_check` names) from `candidate`. Every callable accepts `(rows, lookup, request)`. The implementation is the received and service-verified native Python package `published.a01_r02`.

```python
from candidate import revenue, monthly
rows = [{'region': ' North ', 'units': None, 'price_cents': 5}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
monthly(rows, [], {'fill': 'zero', 'agg': 'sum'})
# []  (missing date is excluded from monthly groups)
```

Inputs are not mutated. `clean` normalizes region strings and fills missing units; fill modes are `zero`, `mean`, `median` (all-missing becomes zero, even median averages central values). `revenue` adds revenue while preserving region spelling. `group` and `monthly` normalize region, group while dropping missing keys, and aggregate nonmissing revenues using `sum`, `mean`, or `count`; monthly keys include the first seven date characters. `lookup` normalizes regions and adds only revenue-per-target, returning `None` for unknown/missing/zero targets or missing revenue. `window` adds a trailing-row mean of nonmissing revenues, with `request.window` of 2, 3, or 4. Outputs retain specified columns and row order where applicable; group outputs are sorted by stringified keys. Invalid modes/sizes raise `ValueError`. Dates are expected as ISO strings.
