# Region target lookup

Public API: `lookup(rows, lookup, request)`. Inputs are lists of row dictionaries, lookup dictionaries containing `region` and `target`, and a request whose `fill` is `zero`, `mean`, or `median`. Returns fresh copies of input rows in order, normalizes string regions with strip/lower, fills missing units, adds `revenue_cents` and `revenue_cents_per_target`. Missing revenue, unknown region, and missing or zero target produce a `None` ratio. Original columns are preserved; target and manager are not added. Inputs are not mutated.

```python
from candidate import lookup
rows = [{'region': ' West ', 'units': 2, 'price_cents': 25}]
result = lookup(rows, [{'region': 'west', 'target': 10, 'manager': 'A'}], {'fill': 'zero'})
# result[0]['revenue_cents_per_target'] == 5.0
```

This package delegates to the verified `published.a00_r02` implementation (which depends on `published.a03_r01`). Inputs are expected to follow the documented table schema.
