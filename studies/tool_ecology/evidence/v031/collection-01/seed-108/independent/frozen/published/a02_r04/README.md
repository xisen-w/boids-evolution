# Row-table services

The package exposes six functions, each with the signature `service(rows, lookup, request)` and returns a new list of dictionaries:

* `clean`: normalize region by stripping/lowercasing and fill missing units.
* `revenue`: fill units and derive `revenue_cents`.
* `group`: aggregate nonmissing revenue by normalized region.
* `monthly`: aggregate by month and normalized region.
* `lookup`: add per-target revenue using exact normalized-region lookup.
* `window`: add a trailing ROWS-window mean of nonmissing revenue.

Example:

```python
from candidate import clean, revenue
rows = [{'region': ' West ', 'units': None, 'price_cents': 125}]
assert clean(rows, [], {'fill': 'zero'})[0]['region'] == 'west'
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

`request.fill` accepts `zero`, `mean`, or `median` (all-missing fills with zero); `request.agg` accepts `sum`, `mean`, or `count`; and `request.window` specifies the trailing row count. Aggregations omit missing revenue and missing group keys. Lookup adds no target or manager columns. Inputs follow the row/lookup/request schema in the service contract. Implementations are reused from `published.a02_r02`; this package adds no independent semantics.
