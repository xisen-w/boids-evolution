# Composable regional sales services

This native Python facade reuses the verified implementations in `published.a06_r04` and adds direct multi-family dispatch. Public services are `clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)`; each returns that family's complete output. The `lookup` function's second argument is the lookup table.

`transform(family, rows, lookup_rows, request)` dispatches a single exact family name. `transform_many(rows, lookup_rows, requests)` accepts a mapping from family names to their family-specific request objects and returns an insertion-ordered mapping of complete outputs. Empty requests produce `{}`; unknown family names raise `KeyError`.

```python
from candidate import transform_many
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
result = transform_many(rows, [], {
    'revenue': {'fill': 'zero'},
    'group': {'fill': 'zero', 'agg': 'sum'},
})
assert result['revenue'][0]['revenue_cents'] == 100
assert result['group'] == [{'region': 'west', 'sum_revenue_cents': 100}]
```

All six services follow their respective service-family specifications (including fill/aggregation options, missing values, sorting, and output columns) and do not mutate input tables. Request schemas and malformed-input behavior are inherited from the underlying implementations; requests must use supported family values (`fill`: zero/mean/median, `agg`: sum/mean/count, `window`: 2/3/4 as applicable).
