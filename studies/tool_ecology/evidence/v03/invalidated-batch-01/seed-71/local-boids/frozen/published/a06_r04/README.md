# Composable row services

Native Python facade over verified `published.a06_r03` adapters. Public service functions `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)` provide the respective full service outputs. `lookup` as a function name shadows no module; its second argument is the lookup table.

`transform(family, rows, lookup_rows, request)` runs one exact family name. `transform_many(rows, lookup_rows, requests)` accepts a mapping from family name to family-specific request and returns `{family: complete_output}` for each entry. Example:
```python
from candidate import transform_many
rows = [{'region':' West ', 'units':2, 'price_cents':50}]
result = transform_many(rows, [], {
    'revenue': {'fill':'zero'}, 'group': {'fill':'zero','agg':'sum'}
})
# result['revenue'][0]['revenue_cents'] == 100
# result['group'] == [{'region':'west','sum_revenue_cents':100}]
```
Family semantics, supported request values, output schemas, and malformed-input behavior are inherited from `published.a06_r03`; this package adds dispatch only. Unknown family keys raise `KeyError`. Inputs are not mutated by the underlying services.
