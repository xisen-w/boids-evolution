# Tabular service helpers

Native Python functions accept `(rows, lookup, request)` and return new dictionaries/lists without mutating inputs. Public adapters: `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`.

`clean` normalizes region via strip/lower and fills missing units. `revenue` fills units and appends `revenue_cents`; it does not normalize the region. `group` and `monthly` normalize region and aggregate nonmissing revenue, emitting sum/mean/count (default sum). `lookup` normalizes region and appends exact normalized-region target division; lookup metadata is not added. `window` appends a trailing row-window mean (default 2). Fill modes are `zero`, `mean`, `median`; all missing values fill as zero. Aggregation modes are `sum`, `mean`, `count`; windows are 2, 3, or 4. Unknown modes raise ValueError. Missing revenue is None.

Example:
```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 50, 'region': ' West ' }]
assert revenue(rows, [], {'fill':'zero'})[0]['revenue_cents'] == 100
```
