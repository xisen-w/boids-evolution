# Row-table service adapters

This package re-exports the dependency-free native implementations in `published.a06_r02` (declared dependency). Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts a list of row dictionaries, lookup records (unused except by the lookup service), and request dictionary; each returns fresh result dictionaries and does not mutate its inputs.

`clean` normalizes region and fills missing units. `revenue` fills units and adds revenue. `group` and `monthly` normalize regions, derive revenue, then aggregate nonmissing revenue using request `agg` (`sum`, `mean`, or `count`). `lookup` normalizes region and adds revenue per region target. `window` derives revenue and trailing-row mean using request `window` width. All fill-capable services accept `fill` of `zero`, `mean`, or `median`; missing values are handled per family specification, including all-missing units filling to zero.

Example:

```python
from candidate import revenue
revenue([{'units': None, 'price_cents': 5}], [], {'fill': 'zero'})
# [{'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```

Inputs are expected to use the documented table schema and valid request options. This package adds no behavior beyond its declared dependency.
