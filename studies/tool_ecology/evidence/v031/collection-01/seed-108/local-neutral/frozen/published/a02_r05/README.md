# Tabular service transforms

This package exposes pure functional adapters `clean(rows, lookup, request)`,
`revenue(rows, lookup, request)`, `group(rows, lookup, request)`,
`monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and
`window(rows, lookup, request)`. Each returns a new list of dictionaries and
preserves its inputs. These entry points delegate to the verified
`published.a02_r04` implementation.

- `clean`: strip/lower regions and fill missing units.
- `revenue`: fill missing units then append `revenue_cents`.
- `group`: normalized region groups, dropping missing region keys.
- `monthly`: month/region groups, dropping either missing key.
- `lookup`: append revenue divided by the exact normalized-region target;
  missing revenue, unknown region, and missing/zero target yield `None`.
- `window`: append trailing ROWS mean of nonmissing revenue, including current.

`request.fill` is `zero`, `mean`, or `median` (default zero; all missing fills
with zero); median averages the middle pair. `request.agg` is `sum`, `mean`, or
`count`; count excludes missing revenue. `request.window` selects trailing row
count. Revenue is units times price in cents and is `None` when either operand
is missing. Original columns and row order are retained for row-wise transforms.

Example:
```python
from candidate import revenue
revenue([{"units": None, "price_cents": 25}], [], {"fill": "zero"})
# [{'units': 0, 'price_cents': 25, 'revenue_cents': 0}]
```
Inputs are expected to be lists of dictionaries and requests dictionaries;
invalid parameter values are rejected by the underlying implementation.
