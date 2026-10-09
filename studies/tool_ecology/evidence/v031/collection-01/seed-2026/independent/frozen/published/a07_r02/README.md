# Native table services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from
`candidate`. Every adapter accepts `(rows, lookup, request)` and returns new
row dictionaries (or grouped result dictionaries); inputs are not modified.

`request` requires `fill` (`zero`, `mean`, `median`); group/monthly also need
`agg` (`sum`, `mean`, `count`); window needs `window` (2, 3, or 4). For example:

```python
from candidate import revenue, group
rows = [dict(id=1, region=' West ', product='x', date='2024-03-10',
             units=None, price_cents=20, cost_cents=2)]
req = {'fill':'zero', 'agg':'sum'}
assert revenue(rows, [], req)[0]['revenue_cents'] == 0
assert group(rows, [], req) == [{'region':'west', 'sum_revenue_cents':0}]
```

Missing units are filled from nonmissing values (even-sized median averages the
middle pair; all-missing becomes zero). Regions are stripped/lowercased except
missing regions. Revenue is units times price, or `None` if price/units is
missing after fill. Row services retain source key order and append derived
keys. Group services drop missing keys, ignore missing revenues, and sort keys
by their string representation. Lookup uses exact normalized region matching;
unknown/missing/zero targets or missing revenue produce `None`. Rolling means
use trailing rows including current, ignoring missing revenues but not extending
the row window. Schemas are expected to follow the service specification and
invalid request options raise `ValueError`.
