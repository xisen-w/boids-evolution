# Sales transformation adapters

Dependency-light native Python adapters reusing the verified `a05_r01` implementation. Every public service has signature `(rows, lookup, request)` and returns fresh row dictionaries without mutating its inputs.

```python
from candidate import clean, revenue, lookup_service
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert clean(rows, [], {'fill': 'zero'})[0]['region'] == 'west'
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

## Adapters

- `clean`: normalize non-null regions using strip/lower and fill missing units; preserve columns and row order.
- `revenue`: fill units and append `revenue_cents` (None when either operand is missing).
- `group`: aggregate nonmissing revenue by normalized region, dropping missing regions.
- `monthly`: aggregate by month (`date[:7]`) and normalized region, dropping missing keys.
- `lookup_service`: append `revenue_cents_per_target` using exact normalized region lookup. Unknown regions and missing/zero targets yield None; no target or manager columns are added.
- `window`: append mean revenue over trailing `request.window` rows including current, ignoring missing revenue values.

Aggregation outputs have keys `region` and `<agg>_revenue_cents`, or `month`, `region`, and that aggregate key for monthly. Groups are sorted lexicographically by stringified keys. Empty sums/counts are zero and empty means None; count excludes missing revenues.

Request parameters: `fill` is `zero`, `mean`, or `median` (even median averages the central pair; all-missing fills with zero); `agg` is `sum`, `mean`, or `count`; `window` is 2, 3, or 4. Their defaults are respectively zero, sum, and 2. Missing values use Python `None`. Input fields are expected to have the types stated by the service contract; malformed row types and unsupported parameter values are not supported.
