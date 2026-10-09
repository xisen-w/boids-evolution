# Table service facade

This package provides six non-mutating row-table adapters, reusing the verified
`published.a01_r01` implementation. Inputs are `(rows, lookup, request)` where
rows and lookup are lists of dictionaries and request supplies `fill` (`zero`,
`mean`, or `median`) and, for aggregates, `agg` (`sum`, `mean`, `count`).
Window requests supply width 2, 3, or 4. Functions preserve specified source
columns and row order for row-oriented outputs. Grouped outputs omit null keys.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' West ', 'date': '2025-03-01', 'units': 2,
         'price_cents': 125}]
request = {'fill': 'zero', 'agg': 'sum', 'window': 2}
assert revenue(rows, [], request)[0]['revenue_cents'] == 250
assert clean(rows, [], request)[0]['region'] == 'west'
```

`lookup` is shadowed by its public family name (not the lookup parameter); use
`candidate.lookup(rows, lookup_rows, request)`. Missing numeric values are handled
according to the service contract. Invalid fill/aggregate/window values raise
`ValueError`. This facade adds no behavior beyond the upstream adapters.
