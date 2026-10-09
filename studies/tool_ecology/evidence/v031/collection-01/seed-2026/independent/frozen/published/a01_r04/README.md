# Tabular service adapters

Native Python package re-exporting the verified implementation in `published.a01_r03`.
There are no third-party requirements. Public call signatures are `clean(rows, lookup, request)`,
`revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. The `lookup` family
function's second argument is a sequence of `{region, target, manager}` records.

`clean` strips/lowercases region and fills missing units. `revenue` fills units and adds
`revenue_cents`, retaining original region. `group` and `monthly` normalize region, derive
revenue, drop missing grouping keys, and aggregate nonmissing revenue. `lookup` normalizes region
and adds `revenue_cents_per_target` (never adds target or manager). `window` derives revenue and
adds the trailing-row mean. Results preserve input order where the service requires it; grouped
results use sorted keys. No function mutates rows, lookup records, or request.

Requests use `fill` = `zero`, `mean`, or `median` (even medians average the central values;
all-missing fills zero); group/monthly also use `agg` = `sum`, `mean`, or `count`; window uses
`window` = 2, 3, or 4. Missing values follow the service contract, including null revenue and
empty-group aggregate rules. Example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
request = {'fill': 'zero', 'agg': 'sum'}
assert revenue(rows, [], request)[0]['revenue_cents'] == 0
assert group(rows, [], request) == [{'region': 'west', 'sum_revenue_cents': 0}]
```

Inputs are expected to follow the specified row schema and valid parameter choices; this API does
not perform schema validation or date parsing beyond using the first seven date characters.
