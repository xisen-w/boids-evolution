# Row-table services

Dependency-free Python adapters. Public functions accept `(rows, lookup, request)` and return newly allocated lists/dictionaries; input objects are not modified. Existing row keys retain their order and derived keys are appended.

- `clean(rows, lookup, request)`: strip/lower non-null region and fill missing units.
- `revenue(...)`: fill missing units and append `revenue_cents` (`None` if either operand is missing); region is otherwise unchanged.
- `group(...)`: normalize region, derive revenue and return region aggregates, dropping null regions.
- `monthly(...)`: as above, grouped by `date[:7]` and region, dropping null keys.
- `lookup_service(...)` (also exported as `lookup`): normalize region, derive revenue, and append `revenue_cents_per_target`. Lookup uses exact region keys; it does not add target/manager.
- `window(...)`: derive revenue and append trailing ROWS mean `roll_revenue_cents`.

`request['fill']` is `zero`, `mean`, or `median` (default `zero`); all-missing units fill with zero. `request['agg']` is `sum`, `mean`, or `count` (default `sum`); count excludes missing revenues. `request['window']` is 2, 3, or 4 (default 2). Empty mean aggregates and windows with no non-null revenues yield `None`; empty sum/count yield zero. Unknown aggregation/fill and invalid window sizes raise `ValueError`.

Example:
```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 35, 'region': 'N'}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 70
```
