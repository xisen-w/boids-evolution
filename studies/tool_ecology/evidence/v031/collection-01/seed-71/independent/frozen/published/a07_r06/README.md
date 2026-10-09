# Table services

Public API: `clean(rows, lookup_rows, request)`, `revenue(rows, lookup_rows, request)`, `group(rows, lookup_rows, request)`, `monthly(rows, lookup_rows, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup_rows, request)`. Each returns new row dictionaries / aggregate dictionaries; inputs are not mutated. `lookup_rows` is only used by `lookup`.

All functions are implemented by the declared dependency `published.a07_r03`. `clean` strips/lowercases regions and fills null units. `revenue` appends revenue_cents, null if units or price is null. `group` and `monthly` aggregate non-null revenue, excluding missing keys. `lookup` appends revenue_cents_per_target (unknown region, null/zero target, or null revenue gives null). `window` appends trailing-row mean revenue, including current row and ignoring null revenues within the window.

Options: request.fill is `zero`, `mean`, or `median` (default `zero`; all-missing -> 0); request.agg is `sum`, `mean`, or `count` (default `sum`; count excludes null revenue); request.window is a positive integer row count (default 2). Empty sums/counts are zero and empty means are null.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
assert group(rows, [], {'fill': 'zero', 'agg': 'count'}) == [
    {'region': 'west', 'count_revenue_cents': 1}
]
```

Rows should provide the documented service schema fields; monthly uses the first seven characters of date strings. The package intentionally relies on `a07_r03` rather than duplicating its implementation.
