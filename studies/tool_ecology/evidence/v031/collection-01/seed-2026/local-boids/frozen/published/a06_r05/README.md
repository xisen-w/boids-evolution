# Table services and dispatcher

Dependency-backed native Python adapters for six table transformations. Each
adapter takes `(rows, lookup, request)` and returns a fresh result without
mutating its inputs. The public functions `clean`, `revenue`, `group`,
`monthly`, `lookup`, and `window` follow the service schemas and semantics in
the publication brief. Fill supports `zero`, `mean`, `median` (all-missing
units fill with zero); aggregation supports `sum`, `mean`, `count`; window
width is supplied in `request['window']`.

`apply(service, rows, lookup_rows, request)` dispatches using one of those six
string names and returns exactly the corresponding adapter result. An unknown
name raises `ValueError`.

```python
from candidate import apply, monthly
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50,
         'date': '2025-01-03'}]
assert monthly(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'month': '2025-01', 'region': 'west', 'sum_revenue_cents': 100}]
assert apply('revenue', rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

Inputs are expected to conform to the documented service schemas and valid
request options. The dispatcher does not coerce or validate table schemas.
