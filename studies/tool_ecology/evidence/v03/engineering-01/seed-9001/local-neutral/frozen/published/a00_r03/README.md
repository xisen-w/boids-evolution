# a00_r03 — verified service facade

Dependency-free facade API (the implementation dependency is `a00_r02`, declared below). Each function accepts `(rows, lookup, request)` and returns the complete result for its named service: `serve_clean`, `serve_revenue`, `serve_group`, `serve_monthly`, `serve_lookup`, and `serve_window`. `SERVICES` maps each family name to its corresponding callable, useful for dispatching requests dynamically.

Example:

```python
from candidate import SERVICES
result = SERVICES['group'](rows, lookup_rows, {'fill': 'median', 'agg': 'sum'})
```

Input semantics, validation, output fields/order, and limitations are those of the delegated `published.a00_r02` APIs; this package performs no additional normalization or mutation.
