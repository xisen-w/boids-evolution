# Table transformations

Native Python APIs (all return new objects and do not mutate inputs):
`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup_rows, request)`.
Rows and lookup tables are lists of dictionaries. `request` requires `fill`
(`zero`, `mean`, or `median`); grouped operations also require `agg`
(`sum`, `mean`, or `count`); window requires `window` (2, 3, or 4).

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 250}]
```

`clean` normalizes region strings (strip/lower) and fills missing units.
Revenue is units times price, or `None` if price is missing. Group and monthly
aggregate nonmissing revenues and drop rows with missing keys; empty sum/count
are zero and empty mean is `None`. Monthly uses the first seven date characters.
Lookup adds revenue per exact normalized region's lookup target; unknown/missing/
zero targets produce `None`. Window adds the trailing-row mean excluding missing
revenues. Missing units are filled from all nonmissing values (median averages
central values); all-missing units become zero. Results preserve row order and
original fields, with derived fields appended. Inputs are expected to follow the
specified table schema; unsupported option values raise `ValueError`.
