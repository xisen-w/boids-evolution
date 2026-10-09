# Row service adapters

Dependency-free public adapter module delegating to `published.a06_r04` (declared dependency). All six functions have signature `(rows, lookup, request)` and return fresh row dictionaries/lists without mutating inputs.

* `clean(rows, lookup, request)`: strip/lower nonmissing region and fill missing units.
* `revenue(rows, lookup, request)`: fill missing units and append `revenue_cents`.
* `group(rows, lookup, request)`: normalized revenue grouped by region.
* `monthly(rows, lookup, request)`: normalized revenue grouped by month and region.
* `lookup(rows, lookup, request)`: normalized revenue and lookup-derived `revenue_cents_per_target`.
* `window(rows, lookup, request)`: revenue plus trailing-row `roll_revenue_cents`.

`request.fill` supports `zero`, `mean`, or `median` (default zero; all missing gives zero); `request.agg` supports `sum`, `mean`, `count` (default sum); `request.window` supports 2, 3, or 4 (default 2). Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```

Group outputs omit null keys; aggregate means with no values are `None`, while empty sum/count are zero. Lookup does not append lookup metadata. Window includes current row and ignores missing revenues within its fixed row span. Input rows are expected to have the service schema; window rejects widths outside 2/3/4.
