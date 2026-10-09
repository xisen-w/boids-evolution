# Tabular service adapters

This package provides six pure, list-of-dictionary service functions. Each accepts
`(rows, lookup, request)` and returns a new list without mutating those inputs.
The implementations are reused from the service-verified `published.a01_r05`
package rather than independently reimplemented.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' North ', 'units': None, 'price_cents': 5}]
clean(rows, [], {'fill': 'zero'})
# [{'region': 'north', 'units': 0, 'price_cents': 5}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```

`clean` normalizes region with strip/lower and fills missing units by zero, mean,
or median (all missing becomes zero; even median averages the middle values).
`revenue` fills units and adds `revenue_cents`, null if either operand is missing.
`group` groups by normalized region; `monthly` groups by month and normalized
region. Both discard missing grouping keys and aggregate nonmissing revenue by
sum, mean, or count; empty sum/count are zero and empty mean is null. Results are
sorted by stringified keys. `lookup` adds `revenue_cents_per_target` from an exact
normalized-region lookup (unknown, absent/zero target, or missing revenue gives
null); target and manager are not copied. `window` adds the trailing-row mean of
nonmissing revenue, including current, using request window size 2, 3, or 4.
`clean`, `revenue`, `lookup`, and `window` preserve input row order and columns,
adding or changing only their documented fields. Requests must specify valid
`fill`, `agg`, or `window` values as applicable; invalid modes/sizes raise
`ValueError`. Dates are expected as ISO date strings.

Each service is also exposed as `<family>_check` for adapter compatibility.
