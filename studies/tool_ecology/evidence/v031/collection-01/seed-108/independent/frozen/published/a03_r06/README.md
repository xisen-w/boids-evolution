# Row-table service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. All return new lists of dictionaries and do not mutate inputs. The `lookup` argument is used by the `lookup` service and may be an empty list for other services.

- `clean`: normalize region using strip/lower and fill missing units, preserving columns and row order.
- `revenue`: fill units and append `revenue_cents` (None when units or price is missing).
- `group`: normalize and calculate revenue, then aggregate by nonmissing region; result columns are `region` and `<agg>_revenue_cents`, sorted by stringified region.
- `monthly`: same revenue calculation, grouped by nonmissing month (`date[:7]`) and region; output sorted by stringified keys.
- `lookup`: append `revenue_cents_per_target` using exact normalized-region lookup keys. Unknown/missing region, absent/zero target, or missing revenue produces None. Target and manager are not appended.
- `window`: append trailing-row `roll_revenue_cents`, the mean of nonmissing revenue values in the last `request['window']` rows including current.

`request` requires `fill` set to `zero`, `mean`, or `median`; all-missing units fill as zero and even medians average the central pair. `group` and `monthly` also require `agg` set to `sum`, `mean`, or `count`; count counts nonmissing revenue. Empty sum/count results are zero and empty means are None. `window` requires a supported size of 2, 3, or 4. Invalid options raise `ValueError`. Inputs are expected to have the service schema and numeric values; no additional schema validation is provided.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'}) == [
    {'region': ' West ', 'units': 2, 'price_cents': 125, 'revenue_cents': 250}
]
```
