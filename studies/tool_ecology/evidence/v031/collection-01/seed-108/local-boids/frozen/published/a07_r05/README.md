# Row service facade

This package provides the six `(rows, lookup_rows, request)` services by delegating to the verified native implementation `published.a03_r04` (dependency declared in `publish.json`). Inputs are not intentionally mutated; row-returning services preserve row order and group services return aggregated rows.

Public callables: `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`; each accepts `(rows, lookup_rows, request)`. `transform(family, rows, lookup_rows, request)` dispatches by one of those six names. Root adapter aliases `clean_service`, `revenue_service`, `group_service`, `monthly_service`, `lookup_service`, and `window_service` have the same three-argument signature.

The delegated contract supports fill `zero`/`mean`/`median` (all-missing becomes zero), aggregation `sum`/`mean`/`count`, and a positive trailing-row window length. Regions are stripped/lowercased; revenues with missing operands are None; unknown/zero lookup targets yield None. Grouping omits missing keys and sorts keys. Invalid options raise `ValueError`.

```python
from candidate import revenue, transform
rows = [{'region': ' West ', 'units': 2, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 50
assert transform('clean', rows, [], {'fill': 'zero'})[0]['region'] == 'west'
```
