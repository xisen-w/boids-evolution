# Tabular transformations

Pure-Python adapters for six tabular service contracts; no dependencies. Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`. Each callable accepts `(rows, lookup_rows, request)` and returns a new list of dictionaries without mutating inputs.

```python
from candidate import revenue, window
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] # 0
window(rows, [], {'fill': 'zero', 'window': 2})
```

`clean` strips/lowercases regions and fills null units. `revenue` fills units and appends `revenue_cents`, without changing region. `group` and `monthly` normalize regions, drop null grouping keys, and aggregate non-null revenue with sum/mean/count; empty sum/count are zero and empty mean is None. `lookup` normalizes regions and appends revenue per target, returning None for absent/zero target or missing revenue; target and manager are not copied. `window` appends the mean of non-null revenue in the trailing physical rows (sizes 2, 3, or 4). Fill modes are zero/mean/median (all-null fills zero; even median averages the central values). Aggregate modes are sum/mean/count. Invalid modes raise ValueError. Existing columns retain their order and appended outputs follow them.
