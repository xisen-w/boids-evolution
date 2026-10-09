# Row-table services

Dependency-backed Python API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns new dictionaries and does not mutate inputs. The implementation is provided by the verified `published.a04_r02` package.

- `clean`: strip/lower region and fill missing units; retain all columns and row order.
- `revenue`: impute units and append `revenue_cents`, missing if units or price is missing.
- `group`: normalize regions, derive revenue, group nonmissing regions and aggregate nonmissing revenues.
- `monthly`: as above, grouped on nonmissing month (`date[:7]`) and region.
- `lookup`: append revenue divided by the exact normalized-region target; unknown/zero/missing targets yield `None`.
- `window`: append trailing row-window mean of available revenue, including current row.

`request.fill` is `zero`, `mean`, or `median` (even medians average the center pair; all-missing becomes zero). `request.agg` is `sum`, `mean`, or `count`; count excludes missing revenue. `request.window` is a positive width. Group outputs are lexically sorted; empty sum/count groups are zero and empty means are `None`.

Example:
```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```
Inputs should be lists of row dictionaries conforming to the service schema. Invalid request values raise `ValueError`.
