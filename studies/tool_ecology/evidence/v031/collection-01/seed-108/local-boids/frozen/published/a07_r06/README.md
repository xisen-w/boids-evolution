# Row service adapters

Native Python package exposing the six row-table service families through a consistent API. It delegates transformations to the received, tested `published.a03_r04` implementation; this package adds no new transformation semantics.

## Public API

Each of `clean(rows, lookup_rows, request)`, `revenue(rows, lookup_rows, request)`, `group(rows, lookup_rows, request)`, `monthly(rows, lookup_rows, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup_rows, request)` runs that family. The six corresponding `*_service` names are thin host adapters with the identical three positional arguments. `transform(family, rows, lookup_rows, request)` dispatches a family string (`clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`).

`rows` and `lookup_rows` are lists of dictionaries; `request` supplies fill (`zero`, `mean`, or `median`), agg (`sum`, `mean`, or `count`) and, for window, window length. Behavior follows the delegated implementation: normalized region strings, missing-value handling, derived revenue, grouping and ordering, lookup handling, and trailing-row windows. Unsupported family/options are not interpreted by this facade and follow the dependency's behavior. The facade does not intentionally mutate inputs.

```python
from candidate import revenue, transform
rows = [{'region': ' West ', 'units': 2, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 50
assert transform('clean', rows, [], {'fill': 'zero'})[0]['region'] == 'west'
```
