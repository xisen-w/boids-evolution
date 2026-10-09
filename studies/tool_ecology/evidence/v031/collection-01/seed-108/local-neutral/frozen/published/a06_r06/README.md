# Sales transformations

Dependency-free native Python services. Public adapters accept `(rows, lookup, request)` with list-of-dict inputs and return new data without mutating inputs.

- `clean(rows, lookup, request)`: strip/lower region and fill missing units using `fill` (`zero`, `mean`, `median`; default zero), all-missing to zero. Retains row and field order.
- `revenue(...)`: fill missing units and append `revenue_cents`; null if units or price is null. Does not normalize region.
- `group(...)`: normalized region revenue aggregation, dropping null region; `agg` is sum/mean/count (default sum), count excludes null revenues.
- `monthly(...)`: group on date prefix YYYY-MM and normalized region; null keys omitted.
- `lookup_service(...)` (alias `lookup`): normalized region, filled revenue and `revenue_cents_per_target`; missing/zero target or missing revenue gives null. Lookup uses normalized region keys; target and manager are not added.
- `window(...)`: append trailing row-window mean of non-null revenues, including current row. `window` defaults to 2.

Group outputs are sorted by stringified keys. Empty sums/counts are zero and empty means null. Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```
