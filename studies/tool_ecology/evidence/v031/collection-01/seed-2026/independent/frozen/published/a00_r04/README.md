# Tabular service adapters

Dependency-backed native Python API exposing six functions with signature
`function(rows, lookup, request)`. Each returns a fresh list of row dictionaries
(or grouped dictionaries); input objects are not mutated. `rows` is a list of
records and missing numeric values are `None`.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'id': 1, 'region': ' West ', 'product': 'x', 'date': '2024-01-02',
         'units': None, 'price_cents': 250, 'cost_cents': 100}]
clean(rows, [], {'fill': 'zero'})
# region='west', units=0; original columns/order retained
revenue(rows, [], {'fill': 'zero'}) # appends revenue_cents
```

`clean` normalizes region via strip/lower and fills units. `revenue` fills units
and appends revenue_cents. `group` and `monthly` normalize, derive revenue, and
aggregate by region or month/region. `lookup` appends revenue_cents_per_target;
unknown regions, missing/zero targets, and missing revenue yield None. `window`
appends a trailing ROWS mean including current, ignoring missing revenues (not
missing rows).

Request keys: `fill` is `zero`, `mean`, or `median` (even medians average the
middle pair; all-missing fills zero); `agg` is `sum`, `mean`, or `count` (count
counts nonmissing revenues); `window` is 2, 3, or 4. Grouping omits missing keys,
uses 0 for empty sum/count and None for empty mean, and sorts by stringified keys.
Original columns retain their order and derived columns append. Invalid policies
raise ValueError. Implementations are supplied by the declared `a00_r01`
dependency; this package adds a stable import surface, not a separate engine.
