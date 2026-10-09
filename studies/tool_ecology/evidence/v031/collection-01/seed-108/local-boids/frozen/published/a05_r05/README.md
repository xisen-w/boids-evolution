# Row-table services

Import the package root and call any service as `service(rows, lookup, request)`.
The six exports are `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.
They are thin adapters to the verified `published.a00_r01` implementation; inputs
are not mutated and returned table shapes follow the service contract.

```python
from candidate import clean, lookup as lookup_service
rows = [{'region': ' West ', 'units': None, 'price_cents': 100}]
result = clean(rows, [], {'fill': 'zero'})
assert result[0]['region'] == 'west' and result[0]['units'] == 0
```

`fill` is zero/mean/median; aggregations are sum/mean/count; window sizes are
2/3/4. Missing values and grouping/lookup behavior follow the service definitions.
This package requires `published.a00_r01` on the Python path and adds no behavior
beyond that dependency.
