# Tabular service adapters

Public functions `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)` are pure
adapters. They return new rows and do not mutate arguments.

`clean` normalizes non-null regions using strip/lower and fills missing units.
`revenue` fills units and adds `revenue_cents`; a missing operand gives None.
`group` groups non-null normalized region and aggregates nonmissing revenue.
`monthly` additionally groups by the first seven characters of date, dropping
missing keys. `lookup` adds `revenue_cents_per_target` using exact normalized
region match; missing/zero target gives None. `window` appends the mean of
nonmissing revenue in trailing ROWS including current. Fill modes are zero,
mean, median (default zero; all-missing -> zero); aggregate modes sum, mean,
count (default sum); window size must be 2, 3, or 4.

Example:
```python
from candidate import revenue
revenue([{'units': None, 'price_cents': 5}], [], {'fill': 'zero'})
# [{'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```
Rows are expected to be dictionaries; dates are expected to be ISO-like strings.
Unknown modes and invalid windows raise ValueError.
