# Row services

Native Python package API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each takes a list of row dictionaries, a lookup list (or `None`), and a request dictionary; each returns a new result and does not mutate inputs.

`clean` normalizes region using strip/lower and fills missing units. `revenue` also appends `revenue_cents`. `group` and `monthly` aggregate nonmissing revenue (dropping missing keys). `lookup` appends revenue per exact normalized region target; it does not append lookup metadata. `window` appends the trailing-row mean. Request options: `fill` is `zero`, `mean`, or `median` (default `zero`; all-missing becomes zero); `agg` is `sum`, `mean`, or `count` (default `sum`); `window` must be 2, 3, or 4. Revenue is null if either operand is null. Empty sum/count groups produce zero; empty mean produces null.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
```

Limitations: input dictionaries are expected to follow the stated row schema; unsupported option values raise `ValueError`. Implementation is provided by the declared dependency `a04_r01`.
