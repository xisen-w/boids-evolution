# Row table services

Pure-Python package; no dependencies. Each public adapter has signature
`family(rows, lookup, request)` and returns newly-created row dictionaries without mutating inputs.
`clean` normalizes string regions with strip/lower and fills null units. `revenue` additionally
adds `revenue_cents`. `group` and `monthly` aggregate non-null revenues (dropping null grouping
keys); monthly adds the first seven date characters as month. `lookup` adds
`revenue_cents_per_target` using normalized region keys. `window` adds a trailing row-window
mean, including the current row and ignoring null revenue values. Fill modes are `zero`, `mean`,
`median` (even medians average the middle pair); an all-null units column fills with zero.
Aggregations are `sum`, `mean`, and `count`; empty sums/counts are zero and empty means null.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

Inputs are lists of mappings; expected schema follows the service contract. Invalid fill,
aggregation, or window values raise ValueError. Missing/non-string region values are retained
as-is except that null grouping keys are dropped.
