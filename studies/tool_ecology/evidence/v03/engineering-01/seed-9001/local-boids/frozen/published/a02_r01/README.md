# table_services

Pure-Python implementations of the six recurring table transformations. Public API functions all accept `(rows, lookup, request)` and return new lists/dictionaries; inputs are not mutated. Supported `request['fill']` values are `zero`, `mean`, `median` (default `zero`); supported `request['agg']` values are `sum`, `mean`, `count` (default `sum`); window sizes are 2, 3, or 4 (default 2).

- `clean(rows, lookup, request)`: normalize region strings and fill units; retains original columns and adds no revenue.
- `revenue(rows, lookup, request)`: same normalization/fill plus `revenue_cents`.
- `group(rows, lookup, request)`: grouped aggregate by nonmissing normalized region.
- `monthly(rows, lookup, request)`: grouped aggregate by month and nonmissing region.
- `lookup(rows, lookup, request)`: derive per-target revenue using the exact normalized region key; no target/manager columns are added.
- `window(rows, lookup, request)`: trailing ROWS mean of nonmissing revenue.

Example: `revenue([{'region':' West ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})` returns `[{'region':'west','units':2,'price_cents':50,'revenue_cents':100}]`.

Rows are expected to be dictionaries with the service schema. Missing units are filled even in the `clean` service. Lookup keys are normalized in the same manner as row regions. Invalid fill/aggregation/window parameters raise `ValueError`.
