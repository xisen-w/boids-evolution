# Row table transforms

Dependency-free Python implementations of the six table services. Public API:
`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`.
Each returns a new list of dictionaries and does not mutate arguments. `clean`
normalizes non-null region strings with strip/lower and fills missing units.
`revenue` fills units and appends revenue_cents. Group and monthly normalize
regions and aggregate nonmissing revenue, dropping null grouping keys.
`lookup` normalizes regions and appends revenue_cents_per_target (lookup keys
are normalized too). `window` adds trailing-row mean revenue; its window is
2, 3, or 4. Fill is zero/mean/median; an all-missing column fills with zero.
Aggregation is sum/mean/count; count excludes missing revenue. Empty aggregate
means and unavailable lookup ratios are None. Original rows and column order
are retained, with derived columns appended.

Example:
```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 30}]
assert revenue(rows, [], {'fill': 'zero'}) == [
    {'units': 2, 'price_cents': 30, 'revenue_cents': 60}]
```
