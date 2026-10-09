# Tabular service adapters

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from this package. Each public function has the exact signature `(rows, lookup, request)` and returns fresh dictionaries (or aggregate dictionaries); input data is not mutated. These stable root-level names delegate to the verified `published.a02_r02` implementations.

* `clean`: normalize nonmissing region strings with strip/lower and fill missing units.
* `revenue`: fill missing units and derive `revenue_cents` (region preserved).
* `group`: normalize region, derive revenue, then aggregate by nonmissing region.
* `monthly`: normalize region, derive revenue and group by nonmissing month and region.
* `lookup`: normalize region, derive revenue and add `revenue_cents_per_target` using exact normalized region lookup.
* `window`: derive revenue and add trailing-ROWS mean `roll_revenue_cents`.

`request['fill']` supports `zero`, `mean`, and `median` (even-sized median averages the middle pair; all-missing fills with zero). Grouped APIs use `request['agg']` = `sum`, `mean`, or `count`; count excludes missing revenue. Window uses `request['window']` = 2, 3, or 4 and includes the current row. Group outputs sort keys as strings; empty means are `None`, and empty sums/counts are zero. Unknown lookup regions, missing/zero targets and missing revenue produce `None`. Inputs are mapping-like rows in the specified schema.

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'north', 'sum_revenue_cents': 100}]
```
