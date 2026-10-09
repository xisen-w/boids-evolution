# Sales table services

This package exposes six pure table transformations: `clean`, `revenue`, `group`,
`monthly`, `lookup`, and `window`. Each callable accepts `(rows, lookup, request)`;
`rows` and `lookup` are lists of dictionaries and `request` is a dictionary. Inputs
are not mutated. Output rows are fresh dictionaries.

```python
from candidate import revenue, group
rows = [{'region': ' WEST ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 250}]
```

`clean` normalizes non-null regions using strip/lower and fills missing units.
`revenue` fills units and adds `revenue_cents`. Fill modes are `zero`, `mean`,
and `median`; all-missing units fill with zero, and even medians average the two
central values. `group` and `monthly` aggregate nonmissing revenue using `sum`,
`mean`, or `count`; monthly groups additionally use the first seven date chars.
Missing grouping keys are excluded. Empty sum/count groups return zero and empty
means return None. `lookup` adds `revenue_cents_per_target`, using normalized,
exact region matching; absent/zero target or missing revenue yields None. It does
not add lookup metadata. `window` adds a trailing-row mean in `roll_revenue_cents`;
window widths are 2, 3, or 4 and null revenues do not contribute to the mean.
Derived revenue is None when units or price is missing. Existing columns are
retained and derived columns appended/replaced by name. Aggregated output is
sorted by stringified keys. This package targets the documented list-of-dicts
sales schema; it does not validate arbitrary schemas.
