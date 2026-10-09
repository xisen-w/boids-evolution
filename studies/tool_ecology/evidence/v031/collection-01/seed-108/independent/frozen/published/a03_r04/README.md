# Row-table service adapters

The package root provides six callables with the identical signature
`function(rows, lookup, request)`, where `rows` and `lookup` are lists of
 dictionaries and `request` is a dictionary. The returned value is a new list
of dictionaries; input objects are not modified. Implementations are delegated
to the received, six-family-verified `published.a03_r03` package.

* `clean`: normalize string regions with strip/lower and fill missing units;
  retains all row fields and order.
* `revenue`: fill missing units and derive `revenue_cents` (null if units or
  price is null); retains all fields and order.
* `group`: normalized region and revenue, then aggregate non-null revenue by
  non-null region. Returns `region` and `<agg>_revenue_cents`.
* `monthly`: group by non-null `date[:7]` month and normalized non-null region;
  returns month, region, and `<agg>_revenue_cents`.
* `lookup`: normalized region/revenue and `revenue_cents_per_target`, using
  region-keyed lookup targets; unknown, null, or zero target gives null.
* `window`: revenue plus trailing-row `roll_revenue_cents` mean, including
  current row and ignoring null revenue values.

Choose `request['fill']` as `zero`, `mean`, or `median` (all missing fills
with zero; even median averages the middle pair). Grouping requires
`request['agg']` of `sum`, `mean`, or `count`; count counts non-null revenue.
Empty sum/count groups are zero and empty means null. Window requires
`request['window']` equal to 2, 3, or 4. Group outputs are sorted by stringified
keys. Revenue and window preserve original region spelling; clean, group,
monthly, and lookup normalize it. No target/manager columns are appended.

Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
result = revenue(rows, [], {'fill': 'zero'})
assert result[0]['revenue_cents'] == 250
```

Rows are expected to have the service's documented tabular keys and numeric
values; invalid fill/aggregation/window options raise `ValueError`. This is a
thin API distribution package, not an independent implementation.
