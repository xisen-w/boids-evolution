# Table transformations

Dependency-backed native Python API: import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`. Each callable has signature `(rows, lookup_rows, request)` and returns fresh output without mutating its inputs. Semantics are provided by the verified `published.a07_r03` package.

`clean` normalizes regions (strip/lower) and fills missing units. `revenue` additionally appends `revenue_cents`. Fill request mode is `zero`, `mean`, or `median` (all missing becomes zero; even median averages the middle pair). Grouping services normalize region and derive revenue, dropping missing grouping keys. `group` groups by region; `monthly` by `date[:7]` and region. Set `request.agg` to `sum`, `mean`, or `count`; count excludes missing revenue. Empty sum/count are zero and empty mean is null. Group outputs sort by stringified keys.

`lookup` appends `revenue_cents_per_target` from exact normalized region lookup. Unknown regions and absent/zero targets or missing revenue yield null. `window` appends trailing-row mean `roll_revenue_cents` over nonmissing revenue, including current row; set `request.window` to 2, 3, or 4.

Example:
```python
from candidate import group
assert group([{'region':' West ', 'units':2, 'price_cents':50}], [],
             {'fill':'zero', 'agg':'sum'}) == [
                 {'region':'west', 'sum_revenue_cents':100}]
```
Input follows the service's list-of-dictionaries schema; date extraction uses the ISO date prefix. The wrapper adds no semantics beyond its declared dependency.
