# Table transformation services

Import any of `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from this package. Each has the exact call signature `(rows, lookup_rows, request)` and returns the service's full list-of-dictionaries output. Input rows, lookup rows, and request are not mutated. The functions delegate to the verified `published.a07_r04` implementation.

* `clean`: normalize region with strip/lower and fill missing units (`fill`: `zero`, `mean`, or `median`; all missing fills with 0).
* `revenue`: clean behavior plus `revenue_cents`, null if units or price is null.
* `group`: normalized region and revenue, grouped by region; `agg` is `sum`, `mean`, or `count` (nonmissing revenue only).
* `monthly`: as group, grouped by ISO date prefix month and region.
* `lookup`: append `revenue_cents_per_target` using exact normalized region matching; unknown/zero/null target or null revenue yields null.
* `window`: append `roll_revenue_cents`, the mean of non-null revenue in trailing `window` rows including current.

Grouped results omit missing keys, sort by stringified keys, use zero for empty sum/count and null for empty mean. Row services preserve input columns/order and append derived columns. Example:

```python
from candidate import group
out = group([{'region': ' West ', 'units': 2, 'price_cents': 50}], [],
            {'fill': 'zero', 'agg': 'sum'})
assert out == [{'region': 'west', 'sum_revenue_cents': 100}]
```

Inputs follow the service list-of-dictionaries schema; dates are expected to use `YYYY-MM-DD`. This API makes no additional validation guarantees beyond the delegated implementation.
