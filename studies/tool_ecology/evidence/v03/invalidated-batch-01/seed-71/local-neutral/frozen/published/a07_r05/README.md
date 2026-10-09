# Row-oriented sales services

Import any service from the package root. Every function has the signature
`service(rows, lookup, request)` and returns a new list of dictionaries without
mutating its arguments. The lookup table is relevant to `lookup` only.

* `clean`: strip/lower region and fill missing units; preserves all columns and order.
* `revenue`: fills units and appends `revenue_cents` (`None` if units or price is missing); preserves region and order.
* `group`: normalizes region, derives revenue, drops missing region keys, and returns sorted `region` plus `<agg>_revenue_cents`.
* `monthly`: as group, grouped by month (`date[:7]`) and region; missing keys are dropped.
* `lookup`: normalizes region and derives revenue, then appends `revenue_cents_per_target`; missing revenue, unknown region, or missing/zero target gives `None`.
* `window`: derives revenue and appends the trailing-rows mean `roll_revenue_cents`.

`request.fill` is `zero`, `mean`, or `median` (default `zero`); all-missing
units fill with zero, and even medians average the two center values.
`request.agg` is `sum`, `mean`, or `count` (default `sum`). Count counts only
nonmissing revenues; empty sums/counts are zero and empty means are `None`.
`request.window` selects trailing row width 2, 3, or 4. Aggregation keys sort
lexicographically by their string representation. Revenue services preserve
original column values except filled units and derived fields.

Example:

```python
from candidate import revenue
rows = [{'region': 'West', 'units': 2, 'price_cents': 150}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 300
```

The API expects ordinary numeric values and valid service modes. This package
re-exports the tested implementation in `published.a07_r04`.
