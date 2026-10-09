# Tabular service adapters

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` from `candidate`. Each has the exact signature `(rows, lookup, request)` and returns a new list of dictionaries. They delegate to `published.a06_r02`; this package therefore declares `a06_r02` as a dependency. Calls do not mutate input rows, lookup records, or request.

* `clean`: strip/lower string regions and fill missing units; preserve columns/order.
* `revenue`: fill units and append `revenue_cents`; leaves region as supplied.
* `group`: normalize region, derive revenue, and aggregate by nonmissing region.
* `monthly`: normalize region and aggregate by nonmissing month and region.
* `lookup`: normalize region, derive revenue and append `revenue_cents_per_target`; target and manager are not added.
* `window`: derive revenue and append `roll_revenue_cents`, the mean of nonmissing revenue over trailing rows including the current row.

`request` supports `fill` (`zero`, `mean`, `median`; default `zero`) and `agg` (`sum`, `mean`, `count`; default `sum`), as applicable. All-missing unit values fill with zero; even medians average the center pair. Group count counts nonmissing revenues; empty sum/count aggregates are zero and empty means are `None`. `window` uses `request.window` (default 2). Lookup returns `None` for unknown region, absent/zero target, or missing revenue. Grouped outputs sort stringified keys. Inputs are expected to follow the specified table schema and supported parameter values.

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': None, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 0, 'price_cents': 50, 'revenue_cents': 0}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'north', 'sum_revenue_cents': 0}]
```
