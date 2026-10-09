# Table service adapters

This package reuses the independently service-verified `a06_r05` native Python
implementations (which in turn depend on `a06_r04`). Public adapters are
`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. The
`lookup` argument is the lookup-row table. Results follow the service schemas:
region normalization and filling, revenue derivation, requested grouping,
monthly grouping, per-target lookup, or trailing-ROWS revenue means,
respectively. Inputs are not mutated. `apply(service, rows, lookup, request)`
dispatches by one of those six names and raises `ValueError` on unknown names.

```python
from candidate import revenue, apply
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert apply('clean', rows, [], {'fill': 'zero'})[0]['region'] == 'west'
```

Options must use the documented request values (`zero`/`mean`/`median`,
`sum`/`mean`/`count`, and window widths 2/3/4). Inputs are expected to conform
to the service schemas; schema validation/coercion is not provided.
