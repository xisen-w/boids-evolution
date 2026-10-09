# Row-table services and batch dispatch

The package re-exports the six verified services and `transform(family, rows, lookup, request)` from `published.a03_r05`. Service adapters `clean_service`, `revenue_service`, `group_service`, `monthly_service`, `lookup_service`, and `window_service` each accept `(rows, lookup, request)` and return that family's full output. Their normalization, fill, aggregation, lookup, window, ordering, and missing-value behavior is exactly that of the dependency.

`transform_many(rows, lookup_rows, jobs)` runs an iterable of `(family, request)` pairs in order and returns corresponding outputs. Inputs are passed unchanged to each service; no cross-job state is kept. Unknown family names raise `ValueError`.

```python
from candidate import transform_many
rows = [{'region': ' West ', 'units': 2, 'price_cents': 25}]
results = transform_many(rows, [], [('clean', {'fill': 'zero'}),
                                    ('revenue', {'fill': 'zero'})])
assert results[0][0]['region'] == 'west'
assert results[1][0]['revenue_cents'] == 50
```

Inputs follow the dependency's documented row schema and supported request options; this package adds no schema coercion or validation beyond batch family-name checking.
