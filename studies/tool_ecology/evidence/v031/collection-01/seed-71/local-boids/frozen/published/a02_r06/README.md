# Row-table service facade

A small native-Python facade over the verified `published.a07_r03` row-table
services. It centralizes family selection and supports running several services.

## API

Every adapter accepts `(rows, lookup, request)` and returns the complete output
for its family. Root callables are `clean`, `revenue`, `group`, `monthly`,
`lookup_service` (the lookup family; named to avoid shadowing its argument), and
`window`. `process(family, rows, lookup, request)` dispatches by family name;
unknown names raise `ValueError`. `process_many(families, rows, lookup, request)`
returns a dictionary keyed by each requested family in iteration order.

```python
from candidate import revenue, process, process_many
rows = [{'region': ' West ', 'units': 2, 'price_cents': 75}]
print(revenue(rows, [], {'fill': 'zero'}))
# [{'region': ' West ', 'units': 2, 'price_cents': 75, 'revenue_cents': 150}]
print(process('clean', rows, [], {'fill': 'zero'}))
print(process_many(['revenue', 'group'], rows, [],
                   {'fill': 'zero', 'agg': 'sum'}))
```

The service contract supports fill `zero`/`mean`/`median`, aggregation
`sum`/`mean`/`count`, and trailing row windows. Transformations preserve input
rows and do not mutate request or lookup data. Exact semantics, including
missing-value behavior and output ordering, are provided by the dependency.
Inputs are expected to be list-of-dict tables; this facade adds no schema
validation and inherits dependency limitations. No external dependencies.
