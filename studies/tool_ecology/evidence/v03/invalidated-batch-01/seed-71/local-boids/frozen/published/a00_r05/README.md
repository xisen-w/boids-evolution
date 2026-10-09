# Composable regional sales services

Native Python facade over the verified `published.a06_r04` services. Public functions `clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)` return the complete output of the corresponding service family. Their fill, aggregation, sorting, missing-value, and output-column semantics are exactly those in the service specification; input objects are not mutated.

`transform(family, rows, lookup_rows, request)` dispatches one exact family name. `transform_many(rows, lookup_rows, requests)` accepts a mapping from family names to independent request dictionaries and returns a mapping to complete outputs; an empty mapping returns `{}`, unknown names raise `KeyError`.

Example:
```python
from candidate import transform_many
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
out = transform_many(rows, [], {
  'revenue': {'fill': 'zero'}, 'group': {'fill': 'zero', 'agg': 'sum'}
})
assert out['revenue'][0]['revenue_cents'] == 100
assert out['group'] == [{'region': 'west', 'sum_revenue_cents': 100}]
```
Limitations: inputs and request values must follow the service family schemas; malformed input behavior is inherited from the underlying implementation.
