# Sales table transformations

This package re-exports the verified native Python transformations from
`published.a03_r04`; it has no independent transformation implementation.

Public APIs (each accepts `(rows, lookup, request)` and returns new lists):

* `clean(rows, lookup, request)` normalizes string regions by strip/lower and
  fills missing units.
* `revenue(rows, lookup, request)` fills units and adds `revenue_cents`, which
  is `None` when price or units is missing.
* `group(rows, lookup, request)` groups normalized nonmissing regions and
  aggregates nonmissing revenue.
* `monthly(rows, lookup, request)` groups by month (`date[:7]`) and normalized
  region, dropping either missing key.
* `lookup(rows, lookup, request)` adds `revenue_cents_per_target` using exact
  normalized region lookup; it does not add target or manager columns.
* `window(rows, lookup, request)` adds the trailing-row mean
  `roll_revenue_cents`.

Rows and lookup are lists of dictionaries. `request` requires `fill` equal to
`zero`, `mean`, or `median`; group/monthly also require `agg` equal to `sum`,
`mean`, or `count`; window requires a row count of 2, 3, or 4. All-missing
units fill with zero; even medians average their middle pair. Group counts count
nonmissing revenues. Empty sum/count groups are zero and empty means are None.
Inputs are not mutated; output row order and original columns are preserved
where applicable. Unsupported options raise `ValueError`.

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 250}]
```
