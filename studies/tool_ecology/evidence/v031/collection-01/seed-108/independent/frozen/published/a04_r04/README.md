# Row-table services

Import the six functions from `candidate`: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts row dictionaries, lookup dictionaries, and a request dictionary and returns a new list without mutating its inputs.

`clean` normalizes region with strip/lower and fills missing units (`zero`, `mean`, or `median`; all missing becomes zero), preserving columns and order. `revenue` fills units and appends `revenue_cents`, preserving region verbatim. `group` normalizes region and groups nonmissing regions, aggregating nonmissing revenue by requested `sum`, `mean`, or `count`. `monthly` additionally groups by the first seven date characters, excluding missing keys. `lookup` adds revenue divided by the exact normalized-region target (None for unknown/zero/missing inputs). `window` adds the mean of nonmissing revenue in the trailing requested number of rows, including current.

Aggregations sort keys lexically by their string representation; output contains only the documented aggregate keys. Unsupported fill falls back to zero and unsupported aggregate to sum. Inputs are expected to follow the specified numeric row schema; monthly dates should be ISO date strings.

Example:
```python
from candidate import revenue
revenue([{'region': ' North ', 'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
