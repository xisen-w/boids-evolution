# Tabular service adapters

Native-Python dispatch facade for the six published tabular services. The
underlying implementation is reused from `published.a07_r03`; this package
adds a uniform family-name dispatcher.

```python
from candidate import apply, window
result = apply("window", rows, [], {"fill": "zero", "window": 3})
# Or call an adapter directly:
cleaned = window(rows, [], {"fill": "median", "window": 2})
```

All adapters take `(rows, lookup, request)` and return the complete family
result without modifying arguments. `apply(family, rows, lookup, request)`
dispatches to `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`;
unknown family names raise `ValueError`. Fill modes are zero/mean/median,
aggregation modes sum/mean/count, and window lengths 2/3/4 per service
contract. The facade introduces no new semantics and relies on the declared
`a07_r03` dependency. Inputs are expected to follow the service schema.
