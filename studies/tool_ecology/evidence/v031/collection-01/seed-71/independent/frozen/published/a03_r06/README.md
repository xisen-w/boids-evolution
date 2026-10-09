# Native row-table transforms

Import any of `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from this package. Each public service function accepts `(rows, lookup, request)` and returns a new list of dictionaries without mutating its inputs.

- `clean`: lowercases and strips string regions and fills null units.
- `revenue`: fills null units and appends `revenue_cents`; region values remain unchanged.
- `group`: normalized-region revenue aggregation, omitting null regions.
- `monthly`: normalized-region and `date[:7]` revenue aggregation, omitting null keys.
- `lookup`: adds revenue divided by the exact normalized-region target; unknown, null, or zero targets produce null.
- `window`: adds the mean non-null revenue in the trailing request-sized row window.

Every function expects request `fill` to be `zero`, `mean`, or `median`; all-null units fill with zero. `group` and `monthly` also require `agg` of `sum`, `mean`, or `count`. `window` requires a window of 2, 3, or 4 rows. Aggregates ignore null revenue (empty sum/count are zero; empty mean is null). Inputs are lists of mapping-like rows, a lookup list for the lookup service, and a request mapping.

Example:

```python
from candidate import revenue
revenue([{'units': 2, 'price_cents': 50, 'region': 'North'}], [], {'fill': 'zero'})
# [{'units': 2, 'price_cents': 50, 'region': 'North', 'revenue_cents': 100}]
```
