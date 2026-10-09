# Row services (verified implementation adapter)

This package exposes six pure row-table services by re-exporting the tested implementation in `published.a03_r02`. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns fresh output dictionaries without mutating inputs. The six corresponding `_service` names are identical aliases.

Rows are lists of dictionaries. `request.fill` accepts `zero`, `mean`, or `median` (all missing units fill as zero); `request.agg` accepts `sum`, `mean`, or `count`; `request.window` controls trailing row count. Regions are stripped/lowercased in clean/group/monthly/lookup. Revenue adds `revenue_cents`; grouping excludes missing keys and ignores missing revenue in aggregates; lookup adds per-target revenue; window adds trailing-row mean. See the upstream implementation documentation for edge semantics; this package adds no behavior beyond that dependency.

Example:
```python
from candidate import revenue
assert revenue([{'units': 2, 'price_cents': 125}], [], {'fill': 'zero'})[0]['revenue_cents'] == 250
```
