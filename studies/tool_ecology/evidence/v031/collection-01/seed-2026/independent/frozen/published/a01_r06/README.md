# Tabular service adapters

Native Python functions accept `(rows, lookup_rows, request)` and return new output without modifying inputs:

- `clean(rows, lookup_rows, request)`: normalize region by strip/lower and fill missing units; preserve all columns/order.
- `revenue(...)`: same fill and add `revenue_cents` (null if units or price is null).
- `group(...)`: normalized region and revenue, aggregate by region dropping missing keys; result has `region` and `<agg>_revenue_cents`.
- `monthly(...)`: as group, keyed by month (`date[:7]`) and region, dropping missing keys.
- `lookup(...)`: normalized region/revenue and `revenue_cents_per_target`, looked up by exact normalized region; target/manager are not added.
- `window(...)`: revenue and `roll_revenue_cents`, trailing ROWS mean including current row.

Request `fill` is `zero`, `mean`, or `median`; all-missing fills with zero and even medians average the central pair. `group` and `monthly` require `agg` in `sum`, `mean`, `count`; count excludes missing revenue. `window` requires a window row count. Aggregate results sort by stringified keys. Empty sum/count aggregates are zero, empty means null. Lookup results are null for unknown region, missing/zero target, or missing revenue. Revenue is null if either operand is null. Month extraction takes the first seven date characters; schemas and date formats are not validated.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
request = {'fill': 'zero', 'agg': 'sum'}
assert revenue(rows, [], request)[0]['revenue_cents'] == 0
assert group(rows, [], request) == [{'region': 'west', 'sum_revenue_cents': 0}]
```
