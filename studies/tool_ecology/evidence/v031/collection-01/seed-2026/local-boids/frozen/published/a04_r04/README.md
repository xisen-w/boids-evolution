# Tabular service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each
accepts rows and lookup as lists of dictionaries and request as a dictionary;
inputs are not mutated. Functions return new row dictionaries for row-wise
services and only the specified key fields for grouped services.

`clean` strips and lowercases string regions and fills missing `units` using
`request['fill']` (`zero`, `mean`, or `median`; default `zero`). Mean/median
use nonmissing units, all-missing resolves to zero, and even median averages
the central pair. `revenue` performs that fill and adds `revenue_cents` as
units times `price_cents`, or `None` if either is missing. `group` normalizes
regions, derives revenue, drops missing region keys, and aggregates nonmissing
revenue by region. `monthly` additionally groups by the first seven characters
of date and drops missing month or region keys. Both grouped functions accept
`request['agg']` (`sum`, `mean`, `count`; default `sum`); count counts nonmissing
revenue, empty sum/count are zero, and empty mean is `None`. Results are sorted
by stringified group keys.

`lookup` normalizes regions, derives revenue, and appends
`revenue_cents_per_target` using exact normalized region matches in lookup.
Unknown regions, missing/zero targets, and missing revenue produce `None`;
target and manager are not appended. `window` derives revenue and appends
`roll_revenue_cents`, the mean of nonmissing revenue within the trailing
`request['window']` rows including the current row (default 2; allowed 2, 3,
4); an all-missing window yields `None`.

Example:
```python
from candidate import revenue
revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
The API is intended for the documented schema and does not validate unrelated
field types.
