# Tabular service helpers

Dependency-free Python functions accepting `(rows, lookup, request)`. Inputs are not mutated; each returns fresh dictionaries.

- `clean(rows, lookup, request)`: normalize region by stripping and lowercasing and fill missing units.
- `revenue(...)`: fill units and append `revenue_cents`; preserves region unchanged.
- `group(...)`: normalized region groups, dropping missing region; appends aggregate revenue values in grouped output.
- `monthly(...)`: group by normalized region and `date[:7]`, dropping missing keys.
- `lookup(...)`: normalized region and per-target revenue using exact normalized region matches.
- `window(...)`: revenue and trailing row-window mean, preserving row order and region.

`request.fill` accepts `zero`, `mean`, or `median` (defaults to zero; all-missing units fill with zero). Aggregation functions use `request.agg` (`sum`, `mean`, `count`, default `sum`). Window uses `request.window` (default 2), a positive integer. Example:

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': None, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 0, 'price_cents': 50, 'revenue_cents': 0}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'north', 'sum_revenue_cents': 0}]
```

The helpers expect rows and lookup records to be mappings with the service schema's keys; malformed non-mapping records are not supported.
