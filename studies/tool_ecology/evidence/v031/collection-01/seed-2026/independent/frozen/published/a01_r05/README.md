# Tabular service adapters

This native Python package exposes six functions, each accepting `(rows, lookup_rows, request)` and returning fresh output without mutating inputs:

- `clean(rows, lookup_rows, request)`: strip/lowercase region; fill missing units. Preserves columns and row order.
- `revenue(...)`: fill units and add `revenue_cents`; retains original columns and order.
- `group(...)`: normalize region, derive revenue, drop missing region keys, and return region plus `<agg>_revenue_cents`, sorted by stringified region.
- `monthly(...)`: as group, grouping by month (`date[:7]`) and region and dropping either missing key.
- `lookup(rows, lookup_rows, request)`: normalize region, derive revenue, and add `revenue_cents_per_target` from exact normalized region lookup; does not append target or manager.
- `window(...)`: derive revenue and add `roll_revenue_cents`, the trailing-row mean including current row.

Use request `{"fill":"zero"}` (also `mean` or `median`) for filling; all-missing units fill with zero and even medians average central values. Group/monthly requests additionally specify `agg` as `sum`, `mean`, or `count`; count counts nonmissing revenue. Window requests specify a row count of 2, 3, or 4. Null revenue propagates when units or price is missing. Lookup yields null for unknown region, missing/zero target, or missing revenue. Empty aggregate groups use zero for sum/count and null for mean. Group outputs are sorted lexicographically by stringified grouping keys.

Example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
request = {'fill': 'zero', 'agg': 'sum'}
assert revenue(rows, [], request)[0]['revenue_cents'] == 0
assert group(rows, [], request) == [{'region': 'west', 'sum_revenue_cents': 0}]
```

Inputs should use the specified row schema and valid request choices. Date handling uses the first seven characters; this API does not validate schemas or parse dates.
