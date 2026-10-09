# Row-table services

A lightweight facade over the verified `published.a03_r02` implementation. Import callable services from `candidate`; each accepts `(rows, lookup, request)` and returns new row dictionaries without mutating its inputs.

* `clean(rows, lookup, request)`: normalize region via strip/lower and fill missing units.
* `revenue(...)`: fill units and add `revenue_cents`.
* `group(...)`: normalized-region aggregation, keyed by `region`.
* `monthly(...)`: aggregation keyed by `month` and `region`.
* `lookup(...)`: adds `revenue_cents_per_target` using normalized region lookup.
* `window(...)`: adds trailing row-window mean `roll_revenue_cents`.

Request options are `fill` (`zero`, `mean`, `median`; default `zero`), `agg` (`sum`, `mean`, `count`; default `sum`) and `window` (positive integer; default 2). Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

Aggregations omit missing revenue values; mean of an empty group is `None`, while sum/count are zero. Grouped services omit missing keys. Original fields are retained for row-wise services. This facade intentionally delegates behavior to its declared dependency; no additional validation or coercion is provided.
