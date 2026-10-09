# Row-table services

This package exposes six pure adapters, each accepting `(rows, lookup, request)` and returning a new list of dictionaries: `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.

```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

`clean` normalizes region strings and fills missing units. `revenue` appends revenue cents. `group` and `monthly` aggregate nonmissing revenue (sum/mean/count) over nonmissing keys. `lookup` adds revenue per target without exposing lookup metadata. `window` adds a trailing-row mean. Fill supports zero/mean/median; all-missing units fill with zero. Window sizes are 2, 3, or 4. Inputs are expected to be service-shaped dictionaries; invalid parameters raise ValueError. Implementations are reused from `published.a03_r03`.
