# Row-table services

Exports six native Python adapters: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns fresh dictionaries and does not mutate its inputs.

`clean` normalizes region by stripping/lowercasing and fills missing units according to request `fill` (`zero`, `mean`, `median`; default `zero`; all-missing fills with 0), preserving columns and order. `revenue` fills units and appends `revenue_cents` (None if units or price is None), without normalizing region. `group` normalizes and derives revenue, excludes missing region keys, and aggregates nonmissing revenue according to `agg` (`sum`, `mean`, `count`; default `sum`); output key is `<agg>_revenue_cents`, sorted by stringified region. `monthly` additionally groups by `date[:7]`, omits missing month/region and sorts by stringified keys. `lookup` normalizes region and adds `revenue_cents_per_target`; unknown regions and missing/zero targets or revenue yield None. `window` derives revenue without normalizing region and adds the mean of nonmissing revenues in the trailing `window` rows (2, 3, or 4, including current); missing rows still consume window positions.

Example:

```python
from candidate import clean, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 4}]
clean(rows, [], {'fill': 'zero'})
# [{'region': 'west', 'units': 0, 'price_cents': 4}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'west', 'sum_revenue_cents': 0}]
```

Inputs are expected to follow the service schema (numeric units/prices, string-or-None region and date, valid parameter choices). No coercion is performed.
