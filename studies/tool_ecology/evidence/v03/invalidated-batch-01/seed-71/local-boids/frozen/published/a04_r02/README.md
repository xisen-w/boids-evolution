# Row-table services

Dependency-free Python adapters; input rows are lists of dictionaries and input objects are not mutated. Import `clean, revenue, group, monthly, lookup, window` from `candidate`. Every adapter accepts `(rows, lookup_rows, request)`; request uses `fill` (`zero`, `mean`, `median`, default `zero`), aggregation `agg` (`sum`, `mean`, `count`, default `sum`), or `window` (2, 3, 4) as applicable.

Example: `revenue([{'units': 2, 'price_cents': 150, 'region': ' North '}], [], {'fill':'zero'})` returns the row with `revenue_cents: 300`; revenue and window retain the input region. `clean` normalizes regions. Grouping services normalize regions and omit missing keys. Lookup rows have region and target; lookup does not append lookup metadata. Missing numeric values are ignored in aggregates; empty sum/count are zero and empty mean is None. Median uses statistics.median. Window is trailing physical rows including current.
