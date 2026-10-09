# Sales row transformations

Native Python, no external dependencies. Public service adapters all have signature `(rows, lookup, request)` and return new dictionaries/lists; inputs are not mutated. Missing numeric values are represented by `None`.

Adapters: `clean` normalizes non-null region strings with strip/lower and fills units; `revenue` fills units and adds `revenue_cents`; `group` and `monthly` aggregate revenue; `lookup` adds `revenue_cents_per_target`; `window` adds trailing-row `roll_revenue_cents`.

Example:
```python
from candidate import revenue
rows = [{'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

`request.fill` supports `zero`, `mean`, `median` (even medians average central values; all-missing resolves to zero). `request.agg` supports `sum`, `mean`, `count`. `request.window` supports 2, 3, or 4 rows. Group results omit missing grouping keys; means of empty/nonmissing-free groups are `None`, sums/counts are zero. Inputs are expected to be row dictionaries with the service's documented fields and `None` for missing values.
