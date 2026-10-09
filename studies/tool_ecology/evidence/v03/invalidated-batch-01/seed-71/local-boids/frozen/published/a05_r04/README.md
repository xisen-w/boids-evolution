# Row-table services and dispatcher

Public adapters `clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`,
`monthly(...)`, `lookup(...)`, and `window(...)` implement the six row-table
services. Each returns fresh output and preserves inputs. The implementations
reuse the verified native implementation in `published.a01_r01`.

`run(family, rows, lookup_rows, request)` dispatches to the corresponding adapter;
`family` must be one of `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`,
otherwise it raises `ValueError`.

```python
from candidate import run
rows = [{'region': ' West ', 'date': '2025-01-02', 'units': 2, 'price_cents': 50}]
assert run('revenue', rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

Fill options are zero/mean/median, aggregations sum/mean/count, and window width
2/3/4. Inputs and request values are expected to follow the service schema.
