# Candidate row services

Public APIs are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. They are thin native-Python service adapters supplied by the declared `published.a04_r04` dependency. They return fresh row dictionaries and do not mutate inputs.

`clean` normalizes region via strip/lower and fills missing units; `revenue` adds `revenue_cents`; `group` and `monthly` aggregate nonmissing revenue, excluding missing grouping keys; `lookup` adds per-target revenue without adding lookup metadata; `window` adds a trailing ROWS mean including current. Options: `fill` is `zero`, `mean`, or `median` (all missing -> zero); `agg` is `sum`, `mean`, or `count`; `window` is 2, 3, or 4. Invalid options raise `ValueError`.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
```

Inputs are expected to follow the service schema: list of dictionaries with numeric units/prices, and lookup rows containing region/target. The package does not validate arbitrary malformed schemas.
