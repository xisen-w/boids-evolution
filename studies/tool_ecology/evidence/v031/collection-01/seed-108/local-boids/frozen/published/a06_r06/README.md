# Row-table services

A small dispatcher over the verified `published.a06_r02` implementation; this package does not duplicate its service logic.

## API

`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)` each execute that service and return its specified output. `run(family, rows, lookup_rows, request)` selects the same APIs by family name (`clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`); an unsupported family raises `KeyError`.

Inputs are lists of row/lookup dictionaries and a request dictionary. Fill (`zero`, `mean`, `median`), aggregation (`sum`, `mean`, `count`), and window width options follow the service specification and are passed through unchanged. Inputs are not intentionally modified. The dispatcher imposes no validation or additional coercion; supported schemas/options and missing-value behavior are those of the dependency.

Example:

```python
from candidate import run
result = run('revenue', [{'region': 'E', 'units': 2, 'price_cents': 7}], [], {'fill': 'zero'})
assert result[0]['revenue_cents'] == 14
```
