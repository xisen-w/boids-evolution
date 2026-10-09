# Native table services

Dependency-free Python APIs; import from `candidate`. Each public adapter has signature
`service(rows, lookup, request)` and returns new dictionaries/lists without mutating inputs.
`request` requires `fill` (`zero`, `mean`, or `median`); group/monthly additionally
require `agg` (`sum`, `mean`, `count`); window requires `window` (2, 3, or 4).

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [dict(id=1, region=' West ', product='x', date='2024-03-10',
             units=None, price_cents=20, cost_cents=2)]
req = {'fill': 'zero', 'agg': 'sum', 'window': 2}
assert clean(rows, [], req)[0]['region'] == 'west'
assert revenue(rows, [], req)[0]['revenue_cents'] == 0
assert group(rows, [], req) == [{'region': 'west', 'sum_revenue_cents': 0}]
```

All original columns and their insertion order are retained for row-oriented outputs;
derived fields are appended. `clean` fills units and normalizes nonmissing regions.
`revenue` adds `revenue_cents`. `group` and `monthly` omit missing grouping keys,
exclude missing revenue from aggregates, and sort keys lexicographically by their string
forms; sum/count of empty valid groups are zero and mean is `None`. `monthly` derives
month from the first seven date characters. `lookup` appends revenue divided by the
exact normalized region key's target, or `None` for unknown/missing/zero target or
missing revenue; manager and target are not added. `window` computes mean over
nonmissing revenues among the trailing rows including the current row (not a count of
last nonmissing observations). Inputs are expected to follow the documented service
schemas and ISO dates. Invalid fill/aggregate/window values raise `ValueError`.
