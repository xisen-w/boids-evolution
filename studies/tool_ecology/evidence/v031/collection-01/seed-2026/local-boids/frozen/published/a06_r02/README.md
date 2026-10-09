# Table service transformations

Dependency-free native Python implementations. Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`; each accepts `(rows, lookup, request)` and returns new row dictionaries without modifying inputs.

`request.fill` is `zero`, `mean`, or `median` (all-missing units fill with 0; even medians average the center pair). `clean` normalizes string regions by strip/lower and preserves columns/order. `revenue` imputes units and appends `revenue_cents`, null when units or price is null. `group` and `monthly` additionally normalize region and return aggregates, dropping missing grouping keys; `monthly` uses the first seven date characters. Set `request.agg` to `sum`, `mean`, or `count`; count counts nonmissing revenue, and empty sum/count are zero while empty mean is null. Results sort by stringified grouping keys.

`lookup` appends `revenue_cents_per_target` from exact normalized region keys; missing/zero targets or missing revenue produce null. `window` appends `roll_revenue_cents`, the mean of nonmissing revenues in trailing `request.window` rows (default 2), including current row; request widths 2, 3, and 4 are supported.

Example:
```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```
Inputs follow the documented service schema; date parsing is intentionally limited to ISO date string prefix extraction.
