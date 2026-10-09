# Row-table service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`.
Each accepts a list of row dictionaries, lookup rows (unused except by `lookup`),
and a request dictionary, returning a new list of dictionaries. These delegate to
the verified `published.a02_r04` implementations (and transitively its declared
`a02_r02` dependency), rather than duplicating semantics.

`clean` normalizes region strings (strip/lower) and fills missing units;
`revenue` adds `revenue_cents`; `group` aggregates by region; `monthly` aggregates
by month and region; `lookup` adds `revenue_cents_per_target`; `window` adds a
trailing-row mean `roll_revenue_cents`. Fill options are `zero`, `mean`, and
`median`; aggregation options are `sum`, `mean`, and `count`; window sizes are
2, 3, and 4. Example:

```python
from candidate import revenue
rows = [{'region': 'West', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

Inputs follow the recurring service schema. Operations do not mutate inputs.
Invalid fill/aggregation/window options raise `ValueError`; missing values follow
the service contract. Lookup matches normalized region keys exactly, and output
columns/order follow each service's contract.
