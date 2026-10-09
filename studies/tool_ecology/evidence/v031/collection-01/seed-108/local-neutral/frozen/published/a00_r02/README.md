# Row-table services

This package provides six pure Python service adapters. Each function accepts
`(rows, lookup, request)` and returns newly allocated output rows without
mutating inputs. The public functions are `clean`, `revenue`, `group`,
`monthly`, `lookup`, and `window`; their semantics and parameter validation
are those of the bundled `published.a05_r01` dependency.

- `clean`: strip/lower non-null regions and fill missing units.
- `revenue`: fill units and add `revenue_cents`.
- `group`: normalize/fill/derive, then aggregate nonmissing revenue by region.
- `monthly`: additionally group on the first seven date characters.
- `lookup`: adds per-target revenue using exact normalized region keys.
- `window`: trailing ROWS mean including the current row.

Fill modes are `zero`, `mean`, and `median`; all-missing units become zero.
Aggregations are `sum`, `mean`, and `count`. Window sizes are 2, 3, or 4.
Invalid options raise `ValueError`. Inputs should be lists of schema-compatible
dictionaries; dates should be ISO strings. Example:

```python
from candidate import revenue
revenue([{'units': None, 'price_cents': 5}], [], {'fill': 'zero'})
# [{'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```
