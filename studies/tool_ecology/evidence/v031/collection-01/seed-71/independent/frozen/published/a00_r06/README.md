# Tabular service facade

This package re-exports the six native adapters verified in `a00_r05`; it adds no transformations of its own. The dependency is required at import time (`PYTHONPATH=/library`).

Each API accepts `rows, lookup, request` and returns a new list without mutating inputs:

- `clean(rows, lookup, request)`: normalize region strings and fill missing units.
- `revenue(rows, lookup, request)`: fill units and derive `revenue_cents`.
- `group(rows, lookup, request)`: aggregate revenue by normalized region.
- `monthly(rows, lookup, request)`: aggregate by month and normalized region.
- `lookup(rows, lookup, request)`: add revenue per exact region target.
- `window(rows, lookup, request)`: trailing row-window mean of revenue.

Example:

```python
from candidate import clean, group
cleaned = clean([{"region": " West ", "units": None}], [], {"fill": "zero"})
summary = group([{"region": " West ", "units": 2, "price_cents": 10}], [], {"agg": "sum"})
```

`fill` supports `zero`, `mean`, and `median` (default `zero`); `agg` supports `sum`, `mean`, and `count` (default `sum`); window width supports 2, 3, or 4 (default 2). Grouped outputs exclude missing keys. Limitations are those of the upstream native API; this facade intentionally does not independently alter or extend it.
