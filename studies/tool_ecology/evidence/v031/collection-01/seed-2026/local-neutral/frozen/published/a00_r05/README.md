# Sales table services

This package exposes six pure service adapters. Each has the signature
`service(rows, lookup, request)` and returns newly constructed output without
mutating inputs. The implementation is provided by the verified dependency
`published.a00_r04`.

- `clean`: normalizes region with strip/lower and fills missing units.
- `revenue`: clean behavior plus `revenue_cents` (`None` if either operand is missing).
- `group`: aggregates nonmissing revenue by normalized region.
- `monthly`: aggregates by month and normalized region.
- `lookup`: adds `revenue_cents_per_target` using exact normalized region lookup.
- `window`: adds trailing-row mean `roll_revenue_cents`.

Fill modes are `zero`, `mean`, and `median`; all-missing fills with zero and
an even median averages its central pair. Aggregate modes are `sum`, `mean`,
and `count`; empty sum/count are zero and empty mean is `None`. Grouped rows
with missing keys are omitted and results are lexically sorted by stringified
keys. Window size is supplied as `request.window`.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
result = revenue(rows, [], {'fill': 'zero'})
assert result[0]['region'] == 'west'
assert result[0]['revenue_cents'] == 0
```
Limitations: inputs are expected to follow the documented table contract; no
schema inference or validation is performed.
