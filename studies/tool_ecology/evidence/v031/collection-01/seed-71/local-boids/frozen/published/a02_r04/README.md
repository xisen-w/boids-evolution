# Row-table service dispatcher

This package re-exports the six verified row-table service adapters from `published.a07_r03` and provides a family dispatcher. It deliberately reuses that implementation rather than duplicating its transformation rules.

## API

`process(family, rows, lookup, request)` accepts a family string (`clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`) and returns the full corresponding result. It raises `ValueError` for an unknown family. The root callables `clean`, `revenue`, `group`, `monthly`, `lookup_service`, and `window` each take `(rows, lookup, request)` and are service adapters.

```python
from candidate import process
result = process('revenue', [{'region': 'West', 'units': 2, 'price_cents': 75}], [], {'fill': 'zero'})
# [{'region': 'West', 'units': 2, 'price_cents': 75, 'revenue_cents': 150}]
```

Options, ordering, normalization, null handling, and errors follow the reused package's documented contract: fill is zero/mean/median (default zero); aggregation is sum/mean/count (default sum); window size is 2, 3, or 4 (default 2). Inputs are not mutated. This package adds no behavior beyond dispatch and therefore inherits any limitations of its dependency.
