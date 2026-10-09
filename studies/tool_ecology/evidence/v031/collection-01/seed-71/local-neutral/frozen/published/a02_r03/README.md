# Tabular transformations

Dependency-backed native Python API re-exporting the verified `published.a02_r02` implementation. Every function accepts `(rows, lookup, request)`, returns new data, and leaves inputs unmodified:

- `clean`: normalize string regions with strip/lower and fill missing units.
- `revenue`: fill units and append `revenue_cents` (without region normalization).
- `group`: normalize region, derive revenue, then aggregate nonmissing revenue by region.
- `monthly`: as group, grouped by month and region.
- `lookup`: normalize region, derive revenue, append exact normalized-key target ratio.
- `window`: derive revenue and append trailing-row mean.

Fill modes: `zero`, `mean`, `median` (even median averages central values; all-missing fills zero). Aggregations: `sum`, `mean`, `count`; count excludes missing revenue. Windows: 2, 3, or 4 rows including current. Aggregation defaults to `sum`, fill to `zero`, and window to 2. Unknown aggregation/fill/window values raise `ValueError`. Revenue is `None` if price or units is missing. Unknown/missing/zero lookup target yields a `None` ratio. Empty grouped sums/counts are zero and means are `None`.

Example:
```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```
