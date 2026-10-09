# Sales-table services

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Inputs are
lists of dictionaries and are not mutated; outputs are fresh list-of-dict rows.

```python
from candidate import revenue, group
rows = [{'region': ' WEST ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 250}]
```

`clean` normalizes non-null regions with strip/lower and fills missing units.
Fill is `zero`, `mean`, or `median`; all-missing fills with zero and even medians
average the central pair. `revenue` adds revenue (None if either operand is
missing). `group` and `monthly` aggregate nonmissing revenue with `sum`, `mean`,
or `count`; monthly groups by the first seven date characters as well as region.
Missing group keys are dropped; empty sum/count yield zero and empty mean None.
`lookup` uses exact normalized region matches and adds revenue per target; unknown
regions, absent/zero targets, and missing revenue yield None. `window` adds the
mean of nonmissing revenue in the trailing `request.window` rows (2, 3, or 4).
Existing columns are retained and derived columns appended/replaced; groups are
sorted by stringified keys. The API is intended for the documented sales schema
and does not validate arbitrary input schemas.
