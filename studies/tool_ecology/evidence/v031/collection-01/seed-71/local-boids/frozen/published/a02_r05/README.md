# Row-table services

Reusable row transformations, delegating the six service definitions to the
verified `published.a07_r03` implementation.

## Public API

All adapters take `(rows, lookup, request)` and return the complete output for
the named family: `clean`, `revenue`, `group`, `monthly`, `lookup_service`, and
`window`. `lookup_service` is named this way to avoid shadowing the lookup
argument. For example:

```python
from candidate import revenue, process
rows = [{'region': ' West ', 'units': 2, 'price_cents': 75}]
print(revenue(rows, [], {'fill': 'zero'}))
# [{'region': ' West ', 'units': 2, 'price_cents': 75, 'revenue_cents': 150}]
print(process('clean', rows, [], {'fill': 'zero'}))
```

`process(family, rows, lookup, request)` dispatches one of `clean`, `revenue`,
`group`, `monthly`, `lookup`, `window`; unknown names raise `ValueError`.
`process_many(families, rows, lookup, request)` returns a dict from each
requested family name to its result, preserving requested insertion order.

Options and semantics (fill, aggregation, missing values, ordering and window
sizes) follow the service contract implemented by the dependency. No external
libraries are required. Inputs are expected to be list-of-dict tables; this
package does not add schema validation, and inherits dependency limitations.
