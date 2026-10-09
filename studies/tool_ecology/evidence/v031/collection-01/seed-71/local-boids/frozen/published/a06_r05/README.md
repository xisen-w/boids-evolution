# Candidate row services

Exports `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)` as pure
row-table adapters. They implement the six recurring service contracts,
including normalization, fill, aggregation, target lookup and trailing ROWS
window behavior. See `published.a06_r04` for detailed inherited service semantics.

`run_service(family, rows, lookup_rows, request)` dispatches one family and
raises `KeyError` for unknown names. `run_services(families, rows, lookup_rows,
request)` evaluates an iterable of names in order and returns a dict keyed by
family; duplicate names overwrite the earlier result. Example:

```python
from candidate import run_services
result = run_services(["clean", "revenue"], rows, lookup_rows,
                      {"fill": "zero", "agg": "sum", "window": 2})
```

No input mutation is intended. The package relies on the verified implementation
in `published.a06_r04` (and its declared transitive dependencies); it adds only
ordered multi-service orchestration.
