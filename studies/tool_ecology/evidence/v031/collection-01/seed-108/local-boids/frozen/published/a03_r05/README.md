# Row-table service facade

This package re-exports the tested `published.a03_r04` service functions and
provides `transform(family, rows, lookup_rows, request)`. All callables take
`(rows, lookup, request)` (except `transform`, which takes the family name
first) and return the corresponding clean, revenue, group, monthly, lookup,
or window result. The service semantics, valid options, missing-value rules,
output ordering, and input-schema limitations are exactly those documented by
the dependency; this package adds no transformations of its own.

```python
from candidate import revenue, transform
rows = [{'region': ' West ', 'units': 2, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 50
assert transform('clean', rows, [], {'fill': 'zero'})[0]['region'] == 'west'
```
