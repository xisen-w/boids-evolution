# Row-oriented table services

Dependency-free native Python package. Public API functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. Every function returns new row dictionaries and does not mutate inputs.

Rows are dictionaries. `clean` normalizes string regions with strip/lower and fills missing units; `revenue` fills units and appends `revenue_cents` without changing original region values. `group` and `monthly` normalize region and aggregate nonmissing revenue by region or (month, region), excluding missing group keys. `lookup` normalizes regions and appends per-target revenue, without appending lookup metadata. `window` appends the mean of nonmissing revenue in the trailing number of rows, while retaining region as provided.

`request.fill` accepts `zero`, `mean`, or `median` (default `zero`; all-missing fills with zero). `request.agg` accepts `sum`, `mean`, or `count` (default `sum`); counts exclude missing revenue. Empty aggregate values are zero for sum/count and `None` for mean. `request.window` is a positive row count (default 2). Monthly dates must support ISO `YYYY-MM-DD` slicing. Lookup rows have region and target; unknown regions, missing/zero targets, and missing revenue yield `None`.

Example:
```python
from candidate import revenue, window
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
assert window(rows, [], {'fill': 'zero', 'window': 2})[0]['roll_revenue_cents'] == 0
```
