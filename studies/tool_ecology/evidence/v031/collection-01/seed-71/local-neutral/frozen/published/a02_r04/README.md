# Tabular transformations

Native Python API re-exporting the service-verified `published.a02_r03` implementation. Every function has signature `(rows, lookup, request)` and returns new dictionaries/lists without mutating inputs.

- `clean`: strip/lower region strings and fill missing units.
- `revenue`: fill missing units and append `revenue_cents`; missing operands produce `None`.
- `group`: normalize region, derive revenue, aggregate nonmissing revenue by nonmissing region.
- `monthly`: as group, grouped by month (`date[:7]`) and region; omit missing keys.
- `lookup`: normalize regions, derive revenue, append `revenue_cents_per_target`; unknown/zero/missing target gives `None`.
- `window`: derive revenue and append trailing-row mean `roll_revenue_cents`.

Fill modes are `zero`, `mean`, and `median` (even median averages the middle pair; all-missing fills with zero). Aggregations are `sum`, `mean`, and `count` (count excludes missing revenue). Window lengths are 2, 3, or 4 rows including current. Defaults are zero, sum, and 2. Invalid modes raise `ValueError`. Empty grouped sums/counts yield zero and means yield `None`.

Example:
```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```
