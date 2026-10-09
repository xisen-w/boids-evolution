# Row services

The package exports `clean(rows, lookup_rows, request)`, `revenue(rows, lookup_rows, request)`, `group(rows, lookup_rows, request)`, `monthly(rows, lookup_rows, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup_rows, request)`. Each returns a new list of row dictionaries and does not mutate arguments. The implementations are delegated to the verified `published.a07_r05` package.

Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

`clean` normalizes region via strip/lower and fills null units by zero, mean or median (all-missing gives zero; even medians average middle values). `revenue` adds revenue_cents, null when units or price is missing. `group` and `monthly` aggregate non-null revenue by normalized region or month/region, dropping missing grouping keys; supported aggregations: sum, mean, count. `lookup` adds revenue_cents_per_target using exact normalized region matching; unknown regions, null/zero targets, and null revenue produce null. `window` adds the trailing ROWS mean including current row. Original columns and row order are retained in row-level services. Dates are expected as ISO strings; invalid parameter values may raise errors.
