# Tabular adapters

Exports six full service adapters, each accepting `(rows, lookup, request)`: `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`. Their schemas and semantics are exactly those of `published.a04_r05`; input rows and lookup are passed through to that implementation. See the service-family specification for fill/aggregation/window parameters and output columns.

`run_service(family, rows, lookup_rows, request)` dispatches one service and raises `ValueError` for an unknown family. `run_many(jobs)` evaluates an iterable of `(family, rows, lookup_rows, request)` tuples in order and returns a list of results; service errors propagate.

```python
from candidate import run_service, run_many
out = run_service("revenue", rows, [], {"fill": "mean"})
outputs = run_many([
    ("clean", rows, [], {"fill": "zero"}),
    ("group", rows, [], {"fill": "median", "agg": "sum"}),
])
```

No extra validation, coercion, or mutation is performed by the dispatcher. Unknown service names are not accepted.
