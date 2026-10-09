# Row-table service facade

This native-Python package provides six services, delegating to the verified `published.a04_r02` implementation. Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns a new list of dictionaries and does not mutate its arguments.

* `clean`: normalize region with strip/lower and impute missing units.
* `revenue`: impute units and append `revenue_cents` (without region normalization).
* `group`: normalize region, derive revenue and aggregate by non-null region.
* `monthly`: additionally group by `date[:7]`, excluding incomplete keys.
* `lookup`: normalized region lookup, appending `revenue_cents_per_target`.
* `window`: append trailing row-window mean `roll_revenue_cents` (without region normalization).

Fill request values are `zero`, `mean`, and `median` (even median averages middle values; all-missing gives zero). Aggregation values are `sum`, `mean`, `count`; count excludes missing revenues. Window width is a positive integer. Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```

Inputs are expected to follow the described list-of-dictionaries schema. Arbitrary schema validation is not provided; invalid fill/aggregation values or invalid window widths raise errors from the implementation.
