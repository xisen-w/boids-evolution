# rowservice facade

This package exposes six pure row-oriented service adapters, reusing the verified `a00_r01` implementation (declared dependency): `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Inputs are lists of dictionaries; results are fresh row dictionaries or aggregate dictionaries, and inputs are not mutated.

`request.fill` accepts `zero`, `mean`, or `median` (default zero); all-missing units become zero. Group/monthly accept `request.agg` of `sum`, `mean`, or `count` (default sum). Window requires `request.window` in 2, 3, 4. Region strings are stripped and lowercased. Aggregates omit missing grouping keys; mean of no revenue is `None`.

Example:
```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'agg': 'sum'}) == [{'region': 'west', 'sum_revenue_cents': 100}]
```
The API assumes the documented service schema and valid numeric values; it does not validate malformed data. `lookup` is both an exported function and its lookup-table argument name.
