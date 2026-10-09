# Row-service adapters

Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. Each returns a new list of dictionaries and does not mutate its inputs. This package re-exports behavior from the declared dependency `published.a00_r01`.

`request.fill` accepts `zero`, `mean`, or `median` (default zero); all-missing units fill with zero. Revenue uses filled units times price, or None if price is missing. Group/monthly accept `request.agg` of `sum`, `mean`, or `count` (default sum); missing group keys are omitted, and means of empty groups are None. `window` requires width 2, 3, or 4 and computes trailing-row means over nonmissing revenues. Region normalization strips whitespace and lowercases strings. Lookup matches the normalized input region against exact lookup region keys, returns None for missing/zero target or missing revenue, and adds no lookup fields.

Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}
]
```

Inputs are expected to follow the documented row schema; malformed numeric values and dates are not validated.
