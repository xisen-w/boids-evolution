# Row-table services

This package re-exports the six verified `published.a01_r01` service adapters
and provides named dispatch. All adapters accept `(rows, lookup_rows, request)`;
inputs are not modified and outputs follow the service family contracts.

```python
from candidate import run, clean, revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert run('clean', rows, [], {'fill': 'zero'})[0]['region'] == 'west'
```

Fill choices are `zero`, `mean`, and `median`; aggregation choices are `sum`,
`mean`, and `count`; rolling windows are 2, 3, or 4. Invalid choices raise
`ValueError`. The underlying service contracts define missing-value behavior.
