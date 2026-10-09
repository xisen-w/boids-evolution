# Native tabular services

The package exports `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. All return fresh dictionaries and do not mutate arguments. Region strings are stripped and lowercased. Missing units are filled from `request['fill']` (`zero`, `mean`, or `median`; default `zero`), with all-missing input filled by zero. Derived revenue is null if units or price is null.

`clean` returns normalized/imputed rows; `revenue` adds `revenue_cents`. `group` groups non-null regions and aggregates non-null revenue according to `request['agg']` (`sum`, `mean`, `count`; default `sum`). `monthly` adds grouping by the first seven date characters as well as region, excluding null keys. `lookup` adds `revenue_cents_per_target` using normalized exact region keys; target itself is not added. `window` adds the mean of non-null revenues among the last `request['window']` rows including current (default 2; accepted sizes 2, 3, 4). Example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 100
```

Inputs are expected to be lists of mappings with the service schema; dates are ISO strings. Aggregation and window parameters outside the documented values raise `ValueError`.
