# Row services and ordered dispatcher

Public functions `clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)` each return the complete result for that service. `transform(family, rows, lookup_rows, request)` dispatches one exact family name; unknown names raise `KeyError`. `transform_many(families, rows, lookup_rows, request)` returns a dictionary mapping requested family names to results in requested insertion order (duplicate keys collapse as in normal dictionaries).

Example:
```python
from candidate import transform_many
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
transform_many(['clean', 'revenue'], rows, [], {'fill': 'zero'})
# {'clean': [{'region': 'west', 'units': 2, 'price_cents': 50}],
#  'revenue': [{'region': 'west', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]}
```

Semantics and validation are inherited from `published.a06_r03`: fill is zero/mean/median (all missing -> 0), aggregates sum/mean/count, groups discard missing keys, lookup uses normalized exact region keys, and windows are trailing ROWS windows including current. Rows/lookup/request are not modified. The dispatcher adds no schema validation; invalid input behavior is inherited from the dependency. `lookup` is the family function name and its second argument is the lookup table.
