# Row services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from
`candidate`. Every function accepts `(rows, lookup, request)` and returns a
new result without mutating its inputs. This thin compatibility package reuses
`published.a07_r04` (declared dependency).

```python
from candidate import revenue, monthly
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

`clean` normalizes regions by strip/lower and fills null units using zero,
mean or median (all-null becomes zero; even medians average the middle pair).
`revenue` adds revenue_cents, null when units or price is null. `group` and
`monthly` aggregate non-null revenue by normalized region or month/region,
dropping missing keys; supported aggregations are sum, mean and count.
`lookup` adds revenue_cents_per_target using exact normalized region lookup;
unknown/missing/zero targets and null revenue yield null. `window` adds the
trailing ROWS mean including current row. Row services preserve original
columns and order. Dates are expected as ISO strings; request parameters must
use the specified fill/agg/window values; invalid values may raise errors.
