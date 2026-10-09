# Tabular service facade

This package re-exports the six tested, pure-Python adapters from `published.a05_r01`.
Every adapter accepts `(rows, lookup, request)` and returns a new result without
mutating its inputs:

* `clean`: normalize non-null region using strip/lower and fill missing units.
* `revenue`: fill units and append `revenue_cents` (null if an operand is null).
* `group`: normalize and derive revenue, then aggregate by non-null region.
* `monthly`: as above, grouped by month and region.
* `lookup`: append revenue per looked-up target, leaving unknown/zero targets null.
* `window`: append trailing-ROWS mean revenue, including current row.

Fill modes are `zero`, `mean`, and `median` (all missing fills with zero); aggregation
modes are `sum`, `mean`, and `count`; window sizes are 2, 3, or 4. Defaults are zero,
sum, and the requested window (window is required). Invalid modes raise `ValueError`.
Input rows should be dictionaries following the service schema; month extraction uses
the first seven characters of the ISO date.

Example:
```python
from candidate import revenue
revenue([{'units': None, 'price_cents': 5}], [], {'fill': 'zero'})
# [{'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```
