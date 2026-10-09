# Row-table adapters

Public functions `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)` are
re-exported from `published.a01_r02`. Inputs are lists of dictionaries; results
are fresh dictionaries and inputs are not mutated. This package depends on
`a01_r02` (and its declared dependency `a01_r01`).

`clean` preserves input columns, normalizes non-null regions, and fills null
units using request `fill` (`zero`, `mean`, or `median`; all-null becomes zero).
`revenue` fills units and appends `revenue_cents`, null if units or price is
null. `group` aggregates non-null revenue by normalized region; `monthly` does
so by month (`date[:7]`) and region. Both accept `agg` (`sum`, `mean`, `count`),
drop missing keys, and sort lexically by stringified keys. `lookup` adds
`revenue_cents_per_target` from exact normalized region matching, null for
unknown/zero/missing targets or null revenue. `window` adds trailing-row mean
`roll_revenue_cents`, including current row, with width from `window`.

Example: `clean([{'region':' NW ', 'units':None}], [], {'fill':'zero'})`
returns `[{'region':'nw', 'units':0}]`. Empty sum/count groups produce zero;
empty means produce null. Requests should use the listed valid choices.
