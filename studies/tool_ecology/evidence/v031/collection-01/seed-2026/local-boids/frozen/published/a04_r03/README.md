# Tabular service adapters

This package exposes six pure-Python adapters, each called as
`function(rows, lookup, request)` and returning new row dictionaries (or grouped
rows) without mutating its inputs:

* `clean`: normalize string regions with strip/lower and fill missing units.
* `revenue`: fill missing units and append `revenue_cents`.
* `group`: normalize region, derive revenue, and group by region.
* `monthly`: normalize region, derive revenue, and group by month and region.
* `lookup`: normalize region, derive revenue, and append
  `revenue_cents_per_target` from exact normalized region matching.
* `window`: derive revenue and append trailing-row `roll_revenue_cents`.

Missing units use `request['fill']` (`zero`, `mean`, or `median`; default
`zero`). All-missing units fill with zero; even medians average their central
values. Aggregation uses `request['agg']` (`sum`, `mean`, or `count`; default
`sum`), ignoring missing revenue. Empty sums/counts are zero and empty means
are `None`. Monthly keys use the first seven date characters; missing group
keys are dropped. Window width is `request['window']` (2, 3, or 4; default 2)
and includes the current row, not the last N nonmissing values. Lookup returns
None for unknown regions, missing/zero targets, or missing revenue, and does
not add target or manager columns. Original columns and row order are preserved
for row-wise functions; grouped results have only their documented keys.

Example:
```python
from candidate import revenue
revenue([{'region': ' West ', 'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'region': ' West ', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```

The adapters accept the specified list-of-dictionaries schema; they do not
validate unrelated column types. Implementation is reused from verified
`published.a04_r02`.
