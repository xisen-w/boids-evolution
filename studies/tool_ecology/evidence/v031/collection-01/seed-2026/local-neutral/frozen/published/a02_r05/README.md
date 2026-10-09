# Candidate row services

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns a new list and is backed by the native Python implementation in the declared `a04_r04` dependency.

Rows are lists of dictionaries. `clean` normalizes region with strip/lower and fills missing units. `revenue` adds `revenue_cents`; group/monthly aggregate nonmissing revenues and omit missing keys; lookup adds per-target revenue based on exact normalized region; window adds trailing ROWS mean including current. Options are `fill` = zero/mean/median (all-missing becomes zero), `agg` = sum/mean/count, and `window` = 2/3/4. Original columns and order are retained for row-oriented results. Lookup metadata is not added. Invalid options raise ValueError.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
```
