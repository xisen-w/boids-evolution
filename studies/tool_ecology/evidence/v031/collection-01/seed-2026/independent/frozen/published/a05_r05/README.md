# Sales table transforms

Native Python, non-mutating adapters. Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. Each takes a list of row dictionaries, lookup rows (unused except by lookup), and a request dictionary, and returns a list of dictionaries.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 150}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' West ', 'units': 2, 'price_cents': 150, 'revenue_cents': 300}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'west', 'sum_revenue_cents': 300}]
```

Missing units are filled by `zero`, `mean`, or `median` (even medians average the middle pair; all-missing becomes zero). Region-based families strip and lowercase regions; `revenue` and `window` retain original region values. Revenue is units times price, or `None` if price/units is missing. Group/monthly omit missing keys; aggregation supports `sum`, `mean`, and nonmissing-value `count`. Monthly uses the first seven date characters. Lookup adds per-target revenue and returns `None` for unknown/missing/zero targets or missing revenue. Window computes the mean of nonmissing revenues within trailing row positions, including current row. Inputs are not mutated. Inputs are expected to follow the service schema; dates are ISO strings and numeric fields numeric. Unknown aggregation/fill values fall back to sum/zero respectively.
