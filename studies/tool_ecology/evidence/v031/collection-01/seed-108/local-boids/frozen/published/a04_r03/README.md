# Tabular service dispatch facade

This package provides a name-based dispatcher and direct service adapters. It
reuses the dependency `published.a06_r02`, whose six native implementations
were verified across the recurring service families.

Public API:

- `run(family, rows, lookup_rows, request)` accepts one of `clean`, `revenue`,
  `group`, `monthly`, `lookup`, or `window`; it returns that service's result.
  An unsupported family raises `ValueError`.
- Direct adapters `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`,
  `monthly(...)`, `lookup(...)`, and `window(...)` expose the corresponding
  family directly. `lookup` in these signatures is the lookup-record list.

Example:

```python
from candidate import run
result = run('group', rows, [], {'fill': 'zero', 'agg': 'sum'})
```

Input schemas, fill/aggregation semantics, output shapes, and limitations are
those of `published.a06_r02`; this facade adds no transformations and does not
mutate its inputs.
