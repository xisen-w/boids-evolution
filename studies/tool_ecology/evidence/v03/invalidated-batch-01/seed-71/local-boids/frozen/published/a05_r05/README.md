# Row-table services

Native Python adapters for `clean`, `revenue`, `group`, `monthly`, `lookup`,
and `window`, plus `run(family, rows, lookup_rows, request)` for dispatch.
The six adapters accept `(rows, lookup_rows, request)` and return fresh rows
(or grouped output), following the recurring service contracts. Fill choices
are `zero`, `mean`, `median`; aggregation choices are `sum`, `mean`, `count`;
window widths are 2, 3, or 4. Invalid choices raise `ValueError`. The dispatcher
raises `ValueError` for unknown family names. Inputs are expected to follow the
specified mapping schema. Implementations reuse verified `published.a01_r01`.

```python
from candidate import run
rows = [{'region': ' West ', 'date': '2025-01-02', 'units': 2,
         'price_cents': 50}]
assert run('revenue', rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```
