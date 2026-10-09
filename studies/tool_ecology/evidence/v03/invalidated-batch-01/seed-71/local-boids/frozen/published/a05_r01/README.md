# Row services

Native Python, no third-party dependencies. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts a list of row dictionaries, a lookup-row list (unused except for `lookup`), and request dictionary; inputs are not mutated.

`clean` fills missing units (`fill`: `zero`, `mean`, or `median`, default `zero`) and normalizes region by strip/lower. `revenue` does the same and appends `revenue_cents`, null when a multiplicand is null. `group` and `monthly` additionally aggregate with `agg` (`sum`, `mean`, `count`, default `sum`); monthly uses the first seven date characters. `lookup` appends `revenue_cents_per_target`, matching the normalized row region exactly against lookup region keys. `window` appends trailing-rows `roll_revenue_cents` with `window` 2, 3, or 4 (default 2). Example:

```python
from candidate import revenue
revenue([{'region':' West ', 'units':None, 'price_cents':5}], [], {'fill':'zero'})
# [{'region': 'west', 'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```

Aggregation ignores null revenue; empty sum/count are zero and empty mean is null. Grouping drops null keys. Other original fields and ordering are retained by row-oriented services; grouped outputs contain only grouping keys and aggregate. Lookup tables are expected to use keys in the same normalized form as row regions. Date values are expected to be ISO strings when non-null.
