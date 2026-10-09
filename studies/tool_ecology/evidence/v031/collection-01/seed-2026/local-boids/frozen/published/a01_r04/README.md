# Tabular service adapters

The package re-exports six tested pure service adapters from `published.a02_r02`.
Each accepts `(rows, lookup, request)` and returns fresh dictionaries (or grouped
result dictionaries), without mutating inputs.

* `clean`: normalize region using strip/lower and fill missing units.
* `revenue`: fill units and derive `revenue_cents`.
* `group`: aggregate revenue by normalized region.
* `monthly`: aggregate by month and normalized region.
* `lookup`: attach `revenue_cents_per_target` from exact region lookup.
* `window`: attach trailing-row mean revenue.

`request` selects `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`,
`count`), or `window` (2, 3, 4) where relevant. Detailed missing-value,
ordering, and aggregation semantics follow the upstream package README.

```python
from candidate import revenue
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
out = revenue(rows, [], {'fill': 'zero'})
assert out[0]['revenue_cents'] == 100
```

Requires `published.a02_r02`; this package adds stable concise import paths and
does not duplicate transformation logic. Inputs are expected to be mappings in
the specified service schema.
