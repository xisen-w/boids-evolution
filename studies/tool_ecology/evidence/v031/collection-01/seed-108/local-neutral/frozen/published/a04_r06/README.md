# candidate

Native Python, dependency-free implementations of the six row-table service adapters. Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts a list of dictionaries, lookup-row list, and request dictionary and returns new dictionaries without modifying arguments.

`request['fill']` selects `zero`, `mean`, or `median` for missing units (even medians average central values; all-missing becomes zero). `request['agg']` selects `sum`, `mean`, or `count`; `request['window']` is 2, 3, or 4. Region strings are stripped and lowercased. Revenue is `units * price_cents`, or `None` if either is missing. Grouped services omit missing group keys; aggregation ignores missing revenues. Lookup adds only `revenue_cents_per_target`, using normalized region keys and returning `None` for absent/zero targets or missing revenue. Window computes trailing physical-row means including current row.

Example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
request = {'fill': 'zero', 'agg': 'sum'}
print(revenue(rows, [], request))
# [{'region': ' West ', 'units': 0, 'price_cents': 25, 'revenue_cents': 0}]
print(group(rows, [], request))
# [{'region': 'west', 'sum_revenue_cents': 0}]
```

Inputs are expected to follow the specified schema and finite numeric values. Unknown fill/aggregation values and unsupported window widths raise `ValueError`.
