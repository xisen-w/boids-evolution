# Row service facade

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_table, request)`, and `window(rows, lookup, request)`.
Each accepts a list of row dictionaries, lookup records (unused except by
`lookup`), and a request dictionary; each returns a fresh result. Implementations
are delegated to verified `published.a04_r02` (declared dependency).

`clean` normalizes region and fills missing units. `revenue` imputes and appends
`revenue_cents` without region normalization. `group`/`monthly` normalize,
compute revenue, and aggregate by their documented keys. `lookup` normalizes,
computes revenue, and appends `revenue_cents_per_target`. `window` computes
revenue without normalization and appends trailing-row mean. Fill modes are
`zero`, `mean`, `median`; aggregation modes are `sum`, `mean`, `count`.

Example:

```python
from candidate import revenue
rows = [{'region': 'N', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

Expected inputs follow the service contract (ordinary numeric values and valid
modes); invalid modes raise `ValueError`. This package intentionally adds no
behavior beyond the dependency's service definitions.
