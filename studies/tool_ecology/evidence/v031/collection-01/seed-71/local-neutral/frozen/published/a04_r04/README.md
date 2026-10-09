# Reusable tabular service adapters

This package re-exports the six tested native Python services from the explicitly declared `a04_r03` dependency. Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns a fresh result and does not mutate its arguments.

- `clean`: strip/lower region strings and fill missing units.
- `revenue`: fill units and derive `revenue_cents`, null when either input is missing.
- `group`: group by normalized region and aggregate nonmissing revenue.
- `monthly`: group by month and normalized region and aggregate nonmissing revenue.
- `lookup`: add per-target revenue using exact region keys; unknown/missing/zero target or missing revenue yields null.
- `window`: add trailing ROWS mean over available nonmissing revenue, including current row.

Requests select fill (`zero`, `mean`, `median`) and aggregation (`sum`, `mean`, `count`); window size is 2, 3, or 4. All-missing fill is zero; an even-sized median averages its two central values. Group outputs drop missing keys and sort stringified keys; count counts nonmissing revenues. Row-preserving services retain original columns/order and append derived fields. Example:

```python
from candidate import revenue
revenue([{"units": None, "price_cents": 5}], [], {"fill": "zero"})
# [{'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```

Inputs are expected to satisfy the service schema and valid parameter choices; arbitrary malformed schemas are not validated here.
