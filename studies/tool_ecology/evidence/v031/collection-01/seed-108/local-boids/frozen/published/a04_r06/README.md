# Row-table service dispatch

A small native-Python facade exposing the six recurring transformations via the verified `published.a06_r02` implementation.

## APIs

Each adapter has signature `(rows, lookup, request)` and returns that family's full output: `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`. Their schemas and option semantics are those in the service specification: fill (`zero`/`mean`/`median`), aggregate (`sum`/`mean`/`count`), and trailing row-window. Inputs are expected to follow the specified row schemas and valid options.

`run(family, rows, lookup, request)` dispatches by family name and raises `ValueError` for unsupported names. `run_many(families, rows, lookup, request)` returns a dict keyed by requested family, evaluating each against the same inputs.

```python
from candidate import run, run_many
result = run('revenue', rows, [], {'fill': 'median'})
results = run_many(['clean', 'group'], rows, [], {'fill': 'zero', 'agg': 'sum'})
```

Results are governed by the delegated implementation; this package adds no altered transformation semantics. `run_many` results are keyed by family, so duplicate names do not create duplicate entries.
