# Row service facade

Dependency-backed, non-mutating adapters for `clean`, `revenue`, `group`,
`monthly`, `lookup`, and `window`. Every adapter accepts `(rows, lookup, request)`
and returns a new list of row dictionaries according to the recurring row
service contracts. Inputs are list-of-dict sales rows, lookup is a list of
region/target/manager dictionaries, and request supplies fill (`zero`, `mean`,
`median`), agg (`sum`, `mean`, `count`), and/or window (2, 3, or 4) as needed.

```python
from candidate import revenue, group
rows = [{'region': 'North', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'north', 'sum_revenue_cents': 100}
]
```

Normalization, missing-value behavior, output columns/order, sorting, and
aggregation follow the underlying `published.a05_r03` services. Invalid request
modes are outside the supported contract and are handled by that dependency.
