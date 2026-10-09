# Row-table service adapters

Public API functions `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)` return
fresh results and do not mutate inputs. The unused lookup parameter is retained
for a consistent adapter signature (except lookup service, where it is the lookup
rows). Implementations are reused from `published.a01_r01`.

`clean` fills missing units and normalizes regions; `revenue` fills units and adds
`revenue_cents`; `group` aggregates by region; `monthly` aggregates by month and
region; `lookup` adds `revenue_cents_per_target`; `window` adds trailing-row mean
`roll_revenue_cents`.

Example:
```python
from candidate import revenue
assert revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```
Fill options are `zero`, `mean`, `median`; aggregations are `sum`, `mean`, `count`;
window widths supported are 2, 3, and 4. Missing revenue operands produce `None`.
Unknown or zero lookup targets produce `None`. Input tables are expected to use the
specified row dictionaries and valid request values; invalid fill/aggregation/window
options raise `ValueError`.
