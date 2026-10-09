# Row-table services

Exports `clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`,
`monthly(...)`, `lookup(...)`, and `window(...)`. Each returns the full family
output as a new list of dicts and leaves inputs unchanged. The APIs implement
region strip/lower normalization, fill policies (`zero`, `mean`, `median`),
revenue in cents, group/month aggregation (`sum`, `mean`, `count`), exact
normalized-region target lookup, and trailing ROWS window means respectively.
See the recurring service contract for exact output columns and null behavior.

Also exports `run(family, rows, lookup_rows, request)` and
`run_many(families, rows, lookup_rows, request)`. Unsupported names raise
`ValueError`; `run_many` returns a dict in requested insertion order (duplicate
names naturally collapse). Example:

```python
from candidate import revenue, run_many
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
request = {'fill': 'zero', 'agg': 'sum', 'window': 2}
assert revenue(rows, [], request)[0]['revenue_cents'] == 250
assert set(run_many(['clean', 'revenue'], rows, [], request)) == {'clean', 'revenue'}
```

Policies follow the specified schema; invalid policy values may raise
`ValueError`. Missing fields are treated as missing by the underlying services.
No dependencies beyond the declared `published.a03_r02` package.
