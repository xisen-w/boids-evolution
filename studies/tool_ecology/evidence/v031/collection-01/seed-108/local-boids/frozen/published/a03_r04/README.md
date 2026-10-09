# Row-table services

Dependency-backed pure-Python transformations. Public service callables all take
`(rows, lookup, request)` and return new records without modifying the inputs:

* `clean`: normalize string `region` (strip/lower), fill missing `units`.
* `revenue`: fill units and append `revenue_cents`.
* `group`: normalized region grouping and revenue aggregation.
* `monthly`: group by month and normalized region.
* `lookup`: append revenue per target found by normalized region.
* `window`: append trailing-rows mean revenue.

`request.fill` is `zero`, `mean`, or `median` (default `zero`; all missing -> 0).
`request.agg` is `sum`, `mean`, or `count` (default `sum`). Missing revenues
are excluded from aggregates; empty mean is `None`, empty sum/count are zero.
`request.window` controls the positive trailing row count (default 2). Group
outputs omit missing keys and are sorted by stringified keys. Row-wise outputs
preserve columns and order, adding only their specified derived fields. Unknown
lookup regions and missing/zero targets produce `None` ratios. Input schemas
are assumed to follow the service contract; invalid options raise `ValueError`.

`transform(family, rows, lookup, request)` dispatches by one of the six names
above and raises `ValueError` for an unknown family.

```python
from candidate import revenue, transform
rows = [{'region': ' West ', 'units': 2, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 50
assert transform('clean', rows, [], {'fill': 'zero'})[0]['region'] == 'west'
```
