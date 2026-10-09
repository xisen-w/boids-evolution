# Tabular row service adapters

Native Python facade over the verified `published.a04_r03` implementation; no third-party dependencies. Public APIs are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup_service(rows, lookup, request)`, and `window(rows, lookup, request)`. The corresponding `serve_*` functions are service adapters with the same signature.

All return fresh output and do not mutate inputs. `clean` normalizes string region values via strip/lower and fills missing units, preserving columns and order. `revenue` fills units and appends `revenue_cents` (does not normalize region). Group, monthly, and lookup normalize region and derive revenue; group/monthly return only aggregate keys and aggregate revenue, dropping missing keys. Lookup adds `revenue_cents_per_target` without adding lookup metadata. Window adds the positional trailing mean `roll_revenue_cents` and does not normalize region. Revenue is null if units or price is null. Fill accepts `zero`, `mean`, or `median` (default zero); all-missing units become zero. Aggregation accepts `sum`, `mean`, or `count` (default sum), with count excluding missing revenue. Window accepts 2, 3, or 4 rows. Aggregate rows sort by stringified keys; empty sum/count are zero and empty mean is null.

Example:
```python
from candidate import revenue
rows = [{'region': 'N', 'units': None, 'price_cents': 10}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```
Inputs should follow the documented row schema and valid request parameter values; malformed schemas are not coerced.
