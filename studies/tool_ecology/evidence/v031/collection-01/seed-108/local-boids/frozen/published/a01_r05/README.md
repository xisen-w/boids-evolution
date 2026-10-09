# Row-table services and dispatcher

Exports `clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)`, plus corresponding `_service` aliases. These implement the six row-table contracts: normalized/fill rows, revenue derivation, grouped and monthly aggregation, target lookup, and trailing-row revenue mean. They return results through the verified `published.a03_r02` implementation and do not mutate inputs.

`run(family, rows, lookup_rows, request)` dispatches one family (`ValueError` for an unsupported family). `run_many(families, rows, lookup_rows, request)` returns a dictionary keyed by family, for example:

```python
from candidate import run, run_many
rows = [{'region': ' West ', 'date': '2025-03-02', 'units': 2, 'price_cents': 125}]
request = {'fill': 'zero', 'agg': 'sum', 'window': 2}
assert run('revenue', rows, [], request)[0]['revenue_cents'] == 250
results = run_many(['clean', 'revenue'], rows, [], request)
```

The `lookup_rows` argument is used by `lookup`; `request` policies are family-specific. Inputs should follow the documented service schema and valid policy values. Batch results preserve the requested family insertion order (as Python dictionaries do); repeated family names produce one result key. No external or network dependencies are required beyond the explicitly declared received package.
