# Tabular transformations

Import the functions with `from candidate import clean, revenue, group, monthly, lookup, window`. Every public callable takes `(rows, lookup, request)` and returns new data without modifying inputs. The implementation is reused from `published.a02_r04` (dependency `a02_r04`).

* `clean`: normalize string regions with strip/lower and fill missing units; preserves columns and order.
* `revenue`: fill missing units and append `revenue_cents`; a missing price or units yields `None`.
* `group`: normalize region, derive revenue, and aggregate nonmissing revenue by nonmissing region.
* `monthly`: as group, grouping by month (`date[:7]`) and region, excluding missing keys.
* `lookup`: normalize region, derive revenue, append `revenue_cents_per_target`; unknown regions, missing/zero targets, or missing revenue yield `None`.
* `window`: derive revenue and append trailing-row mean `roll_revenue_cents` (window includes current row).

Request keys: `fill` is `zero`, `mean`, or `median` (default `zero`); `agg` is `sum`, `mean`, or `count` (default `sum`); `window` is 2, 3, or 4 (default 2). All-missing units fill with zero; even medians average the middle pair. Count counts nonmissing revenue. Empty aggregate groups produce 0 for sum/count and `None` for mean. Invalid modes raise `ValueError`.

Example:
```python
from candidate import revenue
assert revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```
