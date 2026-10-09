# Tabular service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each takes
input rows (a list of dictionaries), lookup rows, and a request dictionary and
returns a new list of dictionaries. Inputs are not mutated. These functions
reuse the published, service-verified `a00_r02` native Python implementation;
no other third-party dependencies are required.

`request.fill` is `zero`, `mean`, or `median` (all missing units fill with 0;
even medians average the middle pair). `clean` fills units and normalizes
regions. `revenue` fills units and adds `revenue_cents`, null if units or price
is null. `group` outputs normalized region and requested sum/mean/count revenue,
dropping missing regions. `monthly` additionally groups on `date[:7]` and drops
missing month or region. `lookup` normalizes row and lookup region keys and adds
`revenue_cents_per_target`; unavailable, null, or zero targets yield null.
`window` adds the trailing inclusive row-window mean of non-null revenue.
Aggregation request values are `sum`, `mean`, `count`; window is 2, 3, or 4.
Original columns are retained where applicable; aggregate outputs contain only
the grouping keys and aggregate column. Revenue/window preserve input region
spelling; clean/group/monthly/lookup normalize it.

Example:
```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```
Dates are interpreted as strings whose first seven characters identify month.
Malformed/missing request parameters are outside the service contract and may
raise `ValueError` or a standard Python exception.
