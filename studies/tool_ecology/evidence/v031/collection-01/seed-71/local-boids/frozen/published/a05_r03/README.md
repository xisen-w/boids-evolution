# Row service facade

This package exposes six pure row-table adapters: `clean(rows, lookup, request)`,
`revenue(rows, lookup, request)`, `group(rows, lookup, request)`,
`monthly(rows, lookup, request)`, `lookup(rows, lookup_table, request)`, and
`window(rows, lookup, request)`. Each returns a newly constructed result and
leaves inputs unchanged. Implementations are delegated to verified native
services in `published.a04_r02` (the declared dependency).

Requests support fill modes `zero`, `mean`, `median`; aggregation modes `sum`,
`mean`, `count`; and trailing window widths 2, 3, or 4. Clean/group/monthly/
lookup normalize region strings; revenue and window preserve region strings.
Missing values, grouping, output columns, and sorting follow those service
contracts. Example:

```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 50, 'region': 'North'}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

Inputs are expected to be lists of dictionaries with the service fields and
valid requests; invalid modes are rejected by the underlying implementation.
