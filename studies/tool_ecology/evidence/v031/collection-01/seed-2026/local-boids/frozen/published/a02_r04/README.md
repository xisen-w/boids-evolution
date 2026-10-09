# Tabular service dispatcher

Dependency-backed facade over the verified `published.a02_r03` implementations; it does not duplicate transformation logic.

Public API: `run_service(family, rows, lookup_rows, request)` dispatches by one of `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`. It returns that family's complete output and raises `ValueError` for an unsupported name. The package root also exports the thin service adapters `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`, each taking `(rows, lookup, request)`.

Example:

```python
from candidate import run_service
result = run_service("revenue", rows, [], {"fill": "zero"})
```

Semantics, output schemas, and parameter requirements are those of `published.a02_r03`; this facade adds no validation or coercion and does not mutate inputs itself.
