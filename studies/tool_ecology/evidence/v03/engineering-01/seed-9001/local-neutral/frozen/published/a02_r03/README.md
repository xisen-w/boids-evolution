# Row-table service adapters

Six root-level functions accept `(rows, lookup, request)` and return a new list of dictionaries without mutating arguments:
`clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`. These are re-exports of the verified implementation in `published.a02_r01`.

`clean` normalizes non-null region strings and fills missing units. `revenue` fills missing units and adds revenue cents. `group` aggregates nonmissing revenue by normalized region; `monthly` aggregates by month and normalized region. Both drop missing grouping keys. `lookup` adds revenue per exact region target, and `window` adds a trailing-row revenue mean.

Request options: `fill` is `zero`, `mean`, or `median` (all missing units become zero; even median averages central values); `agg` is `sum`, `mean`, or `count` (count excludes missing revenue); `window` is the trailing row width. Missing operands produce `None`; unknown/zero lookup targets produce `None`. Empty sum/count aggregates are zero and empty means are `None`. Output sorting and column preservation follow the service contract. No schema validation or value coercion is performed.

```python
from candidate import revenue, group, lookup as lookup_service
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {})[0]['revenue_cents'] == 250
assert group(rows, [], {'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 250}
]
```
