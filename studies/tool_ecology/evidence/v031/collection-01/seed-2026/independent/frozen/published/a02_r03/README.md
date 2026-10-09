# Tabular service adapters

This package exposes six root callables, each taking `(rows, lookup, request)` and returning a fresh list of dictionaries: `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`. Implementations are reused from the verified `published.a02_r02` dependency.

- `clean`: normalized region and filled units; all other columns retained.
- `revenue`: filled units and derived `revenue_cents`.
- `group`: normalized region, derived revenue, then aggregate by region.
- `monthly`: normalized region and aggregate by month and region.
- `lookup`: normalized region and adds `revenue_cents_per_target`.
- `window`: adds trailing row-window mean `roll_revenue_cents`.

Requests use `fill` = `zero`, `mean`, or `median`; aggregations use `agg` = `sum`, `mean`, or `count`; window requests use `window` = 2, 3, or 4. Example:

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 100
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
```

Inputs are not mutated. Revenue/window preserve region as provided; grouping and lookup normalize it. The underlying implementation does not validate malformed dates or unsupported request values.
