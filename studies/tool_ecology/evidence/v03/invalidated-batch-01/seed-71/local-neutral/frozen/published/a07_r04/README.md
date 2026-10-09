# Row services

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`.
All return new dictionaries and do not mutate arguments. `lookup` parameter is
ignored except by the lookup service. This package re-exports the tested native
implementations in `published.a07_r02`.

`clean` strips/lowercases regions and fills missing units. `revenue` fills units
and adds revenue_cents while retaining original region. `group`/`monthly`
normalize regions and aggregate revenue; monthly also derives YYYY-MM from date.
`lookup` adds revenue_cents_per_target using normalized region keys.
`window` adds the trailing-row mean roll_revenue_cents. Fill modes are zero,
mean, median (default zero); all-missing fills are zero. Aggregations are sum,
mean, count (default sum). Missing group keys are dropped; empty aggregate
sum/count are zero and mean is None. Unknown/missing/zero lookup targets produce
None. Window widths supported are 2, 3, and 4. Invalid modes raise ValueError;
numeric input types are expected.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 150}]
assert revenue(rows, [], {'fill': 'zero'}) == [
    {'region': ' West ', 'units': 2, 'price_cents': 150, 'revenue_cents': 300}
]
```
