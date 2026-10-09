# Tabular services facade

This dependency-backed package exposes verified native services from `published.a02_r02` through a stable root API. Every function accepts `(rows, lookup, request)` and returns a fresh list; inputs are not mutated.

Public functions: `clean`, `revenue`, `group`, `monthly`, `lookup_service`, and `window`. `lookup_service` is named thus because `lookup` is its second argument. `clean` normalizes region and fills units; `revenue` fills and derives revenue; `group` and `monthly` aggregate; `lookup_service` adds revenue per target; `window` adds a trailing row mean. Fill choices are zero/mean/median; aggregations sum/mean/count; window sizes 2/3/4. Missing values and empty-input behavior follow the underlying service API.

Example:
```python
from candidate import revenue
revenue([{'units': 2, 'price_cents': 10, 'region': 'X'}], [], {'fill': 'zero'})
# [{'units': 2, 'price_cents': 10, 'region': 'X', 'revenue_cents': 20}]
```
For the family adapter interface (including a function literally named `lookup`), use `from published.a02_r02 import lookup`.
