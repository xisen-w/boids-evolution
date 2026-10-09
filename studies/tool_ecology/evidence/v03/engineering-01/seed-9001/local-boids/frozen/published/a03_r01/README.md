# Table services

Native Python, no third-party dependencies. Public APIs are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts a list of row dictionaries, a lookup list (unused except by the lookup service), and a request dictionary. Inputs are not mutated; returned row dictionaries are copies.

`request.fill` is `zero`, `mean`, or `median` (default `zero`); missing units are imputed from the table, with all-missing data filled by zero. `request.agg` is `sum`, `mean`, or `count` (default `sum`). `request.window` is 2, 3, or 4 (default 2). For example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 5}]
revenue(rows, [], {'fill': 'zero'})  # [{'region': 'west', 'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})  # [{'region': 'west', 'sum_revenue_cents': 0}]
```

Clean and row-preserving services retain input keys and row order. Grouping emits only its documented aggregate fields and excludes missing group keys. Lookup expects lookup dictionaries with `region` and `target`; manager is ignored. Null/non-numeric values outside the specified input contract are not specially handled.
