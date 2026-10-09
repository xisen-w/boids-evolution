# Row-table services

Native-Python adapters for six row-dictionary transformations. Import from `candidate`; every service has the API `service(rows, lookup, request)` and returns a new list without mutating inputs. Inputs use the documented row fields (`region`, `date`, `units`, `price_cents`) and lookup entries (`region`, `target`, `manager`).

- `clean`: strip/lower region and fill missing units using request `fill` (`zero`, `mean`, `median`; all-missing becomes 0), preserving columns and order.
- `revenue`: fill units and append `revenue_cents` (None when either operand is missing), preserving original region.
- `group`: normalize region, derive revenue, discard missing region keys, aggregate nonmissing revenue by `agg` (`sum`, `mean`, `count`), sorted by stringified region.
- `monthly`: group by ISO date's `YYYY-MM` and normalized region, dropping missing group keys; same aggregation and sorting by stringified keys.
- `lookup`: normalize region, derive revenue, and append revenue divided by its exact-region target; unknown regions, missing/zero targets, or missing revenue produce None.
- `window`: derive revenue and append the mean of nonmissing revenue among trailing `window` rows including current.

Aggregates contain only the group keys and `<agg>_revenue_cents`. Example:

```python
from candidate import revenue
rows = [{'region': ' N ', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' N ', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```

Unsupported fill/aggregate values follow the underlying implementation's documented fallbacks (zero/sum). Numeric inputs are expected to be numeric or None; monthly dates are expected as ISO strings. This package delegates to the received, verified `a04_r04` implementation.
