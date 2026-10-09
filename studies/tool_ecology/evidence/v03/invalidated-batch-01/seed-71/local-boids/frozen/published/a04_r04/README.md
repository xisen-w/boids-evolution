# Row-table services and dispatcher

Public APIs `clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`,
`monthly(...)`, `lookup(...)`, and `window(...)` return the complete output of
the corresponding service. `transform(family, rows, lookup_rows, request)`
selects by exact family string (`clean`, `revenue`, `group`, `monthly`,
`lookup`, `window`) and raises `KeyError` for unknown values.

Example:
```python
from candidate import transform
transform('revenue', [{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```

Request options are `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`,
`count`), and `window` (2/3/4). Semantics, missing-value treatment, output
ordering, and input immutability follow the verified `published.a06_r03`
implementation. This facade adds dispatch, not validation; invalid schemas or
option values have no additional guarantees.
