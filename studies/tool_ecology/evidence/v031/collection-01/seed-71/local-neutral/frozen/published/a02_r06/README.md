# Table services

Pure Python implementations, with no external dependencies. Public adapters all have signature `(rows, lookup, request)` and do not mutate arguments:

- `clean(rows, lookup, request)` normalizes nonmissing regions and fills missing units.
- `revenue(...)` fills units and appends `revenue_cents`.
- `group(...)` returns region aggregates.
- `monthly(...)` returns month/region aggregates.
- `lookup(...)` appends `revenue_cents_per_target` using region targets.
- `window(...)` appends the trailing row-window revenue mean.

Fill modes are `zero`, `mean`, and `median`; aggregation modes are `sum`, `mean`, and `count`. The request window is a positive row count (service values 2, 3, or 4). Example:

```python
from candidate import revenue
rows = [{'id': 1, 'region': ' West ', 'product': 'x', 'date': '2024-01-01',
         'units': None, 'price_cents': 25, 'cost_cents': 4}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 0
```

Rows are expected to use the documented service schema and numeric amounts. Null group keys are excluded; aggregation count counts non-null revenues. Lookup matching normalizes region strings on both sides; absent/null/zero targets yield a null ratio. The package does not add target or manager columns.
