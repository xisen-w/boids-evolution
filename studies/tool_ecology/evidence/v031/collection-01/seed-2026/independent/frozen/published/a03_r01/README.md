# Tabular services

Native Python, no third-party dependencies. Public API consists of six functions in the package root, each with signature `family(rows, lookup, request)` and returning new dictionaries/list without mutating arguments:

- `clean(rows, lookup, request)`: fills null `units` and normalizes string regions (`strip().lower()`), retaining columns/order.
- `revenue(...)`: same preparation, plus `revenue_cents` (`units * price_cents`, or null if either is null).
- `group(...)`: groups prepared revenue by normalized region, drops null regions, and returns sorted dictionaries with `region` and `{agg}_revenue_cents`.
- `monthly(...)`: groups by month (`date[:7]`) and region, drops null keys, and returns sorted `month`, `region`, `{agg}_revenue_cents` dictionaries.
- `lookup(...)`: adds `revenue_cents_per_target`; exact match between the normalized input region and lookup row's `region`; missing revenue/target or zero target gives null. Lookup keys are not normalized.
- `window(...)`: adds rolling mean revenue over trailing `window` rows including current, ignoring null revenues.

`request` requires `fill` equal to `zero`, `mean`, or `median`; all-null units are filled with zero, and even medians average their two center values. Group services require `agg` equal to `sum`, `mean`, or `count`; count counts non-null revenues. Empty sum/count groups are naturally zero, while empty mean is null. Window requires 2, 3, or 4. Example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
request = {'fill': 'zero', 'agg': 'sum'}
assert revenue(rows, [], request)[0]['revenue_cents'] == 0
assert group(rows, [], request) == [{'region': 'west', 'sum_revenue_cents': 0}]
```

The functions assume rows and lookup are iterable collections of mappings with the documented input fields. They do not validate arbitrary malformed dates or nonnumeric values; such inputs may raise normal Python errors. `lookup` uses the input's normalized region as an exact lookup key.
