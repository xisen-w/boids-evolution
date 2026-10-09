# Tabular service adapters

This package provides six pure-Python adapters and a small family dispatcher. Public service functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. Each returns a new list of row dictionaries; inputs are not mutated. `run(family, rows, lookup_rows, request)` invokes one adapter by its family name and raises `ValueError` for unknown names.

Fill values use `request['fill']` (`zero`, `mean`, or `median`; all-missing units fill with zero). Aggregations use `request['agg']` (`sum`, `mean`, or `count`, counting nonmissing revenue). Window uses `request['window']` (2, 3, or 4 trailing rows including current). Region-normalizing families strip and lowercase strings. Group/monthly omit missing grouping keys; lookup produces `None` for unavailable revenue or target and does not append lookup metadata. Revenue is `None` if units or price is missing. Inputs are expected to follow the service schema and valid request options.

Example:
```python
from candidate import revenue, run
rows = [{'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert run('clean', rows, [], {'fill': 'zero'})[0]['units'] == 2
```
