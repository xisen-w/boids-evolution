# Table service facade

This dependency-light package re-exports the six pure-Python list-of-dict adapters from `published.a02_r01`; it adds no alternate implementation. Input rows, lookup rows, and request are not mutated. All APIs have signature `(rows, lookup, request)` and return a new list.

* `clean`: normalize non-null region by strip/lower and fill missing units.
* `revenue`: fill missing units and add `revenue_cents`.
* `group`: normalized revenue grouped by region, aggregate chosen by `request['agg']`.
* `monthly`: normalized revenue grouped by month and region.
* `lookup`: normalized revenue plus exact-region target ratio.
* `window`: revenue plus trailing-row mean.

`request['fill']` accepts `zero`, `mean`, or `median` (defaults to zero); all-missing units fill with zero. `agg` accepts `sum`, `mean`, or `count` (defaults to sum). `window` is trailing row width (defaults to 2). Derived values are None when operands are missing; unknown/zero target ratios are None. Aggregates drop missing grouping keys; empty sum/count are zero and empty mean is None. For example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' West ', 'units': 2, 'price_cents': 125, 'revenue_cents': 250}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'west', 'sum_revenue_cents': 250}]
```

The facade exposes only these row-table functions; it does not validate schemas or coerce values. The received implementation is the sole source of behavior.
