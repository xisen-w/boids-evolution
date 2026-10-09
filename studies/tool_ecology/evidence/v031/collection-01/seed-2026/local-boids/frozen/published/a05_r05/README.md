# Tabular service adapters

Import the six functions from `candidate`: `clean(rows, lookup, request)`,
`revenue(rows, lookup, request)`, `group(rows, lookup, request)`,
`monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and
`window(rows, lookup, request)`. Inputs are lists of dictionaries and are not
mutated; row-wise functions return copied dictionaries, grouped functions
return only their documented keys.

`clean` normalizes string regions using strip/lower and fills missing units.
`revenue` fills units and appends `revenue_cents`, null if units or price is
null. Fill mode is request `fill`: `zero`, `mean`, or `median` (default zero);
missing values are excluded from statistics, all missing becomes zero, and
even medians average the middle pair.

`group` normalizes regions and groups non-null regions. `monthly` additionally
groups by date prefix YYYY-MM; missing keys are dropped. Both use request
`agg` (`sum`, `mean`, or `count`, default sum), excluding missing revenues;
empty sum/count are zero and empty mean is null. Output ordering is sorted by
stringified group keys.

`lookup` adds `revenue_cents_per_target` based on exact normalized region
matching. Unknown region, null/zero target, or null revenue gives null; lookup
manager/target fields are not appended. `window` adds `roll_revenue_cents`,
the mean of nonmissing revenues among the trailing request `window` rows
(including current; default 2, accepted widths 2/3/4). A wholly missing
window gives null.

Example:
```python
from candidate import revenue
rows = [{'region': 'West', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': 'West', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
The API targets the documented input schema and does not validate arbitrary
field types.
