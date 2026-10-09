# Row services

Pure native-Python adapters for the six row-table service families. Public API:
`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. All return new dictionaries/lists; inputs are not mutated. Requests use `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`), or `window` (2, 3, 4) as applicable.

Example: `revenue([{'region':' EAST ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})` returns a row with normalized region `east`, units `2`, and revenue_cents `100`, retaining supplied columns. Group outputs `{region, <agg>_revenue_cents}`; monthly outputs `{month, region, <agg>_revenue_cents}`. Lookup input entries are `{region,target,manager}` and only target is used; output does not add target/manager. Missing values use `None`; mean of an empty group is `None`. Invalid request options raise `ValueError`. Values are assumed numeric where arithmetic is required, and dates are assumed ISO strings.
