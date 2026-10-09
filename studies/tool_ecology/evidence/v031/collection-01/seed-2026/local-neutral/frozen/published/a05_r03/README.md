# Sales row transformations

Native-Python service adapters reusing the tested `a05_r01` implementation. Inputs are lists of row dictionaries, lookup dictionaries, and a request dictionary; each call returns fresh rows and does not mutate inputs.

```python
from candidate import clean, revenue, lookup_service
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert clean(rows, [], {'fill': 'zero'})[0]['region'] == 'west'
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

Public adapters: `clean(rows, lookup, request)` normalizes region and fills units; `revenue(...)` fills units and adds `revenue_cents`; `group(...)` and `monthly(...)` aggregate nonmissing revenue by normalized region, or month and region, respectively; `lookup_service(...)` appends revenue divided by the exact normalized region target; `window(...)` adds trailing-row mean revenue. Aggregate outputs contain grouping keys and `<agg>_revenue_cents`. Lookup does not add target/manager.

Request keys: `fill` is `zero`, `mean`, or `median` (even median averages central values; all-missing fills zero); `agg` is `sum`, `mean`, or `count` (count excludes missing revenue); `window` is 2, 3, or 4 and includes current row. Defaults are zero, sum, and 2. Missing revenue operands, missing/zero lookup targets, and empty means result in `None`; empty sums/counts are zero. Missing grouping keys are dropped. Regions are stripped and lowercased. Malformed field types and unsupported request values are outside the API contract. The lookup adapter uses `lookup_service` to distinguish the callable from its lookup-table argument.
