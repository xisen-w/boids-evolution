# Row services

This package provides six pure row-table adapters, backed by the verified native implementation `published.a06_r03` (declared dependency): `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. They return fresh dictionaries and do not mutate inputs.

`clean` normalizes region with strip/lower and fills missing units using request `fill` (`zero`, `mean`, or `median`; all-missing becomes 0). `revenue` appends revenue_cents, null when units or price is null. `group` and `monthly` normalize region, calculate revenue, drop missing grouping keys, and aggregate non-null revenue using request `agg` (`sum`, `mean`, `count`). `lookup` normalizes region and adds revenue_cents_per_target using exact region-key matching; unknown, null/zero target, or null revenue yields null. `window` appends the trailing ROWS mean using request `window` (2, 3, or 4), counting the current row and skipping null revenues.

Example:
```python
from candidate import revenue
revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```

Inputs should follow the documented schemas and parameter modes; invalid modes raise ValueError. Lookup keys are exact (input regions are normalized, lookup keys are not). No target or manager fields are added.
