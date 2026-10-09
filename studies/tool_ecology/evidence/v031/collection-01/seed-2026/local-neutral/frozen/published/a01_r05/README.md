# Row-table transformations

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Inputs are
lists of row dictionaries, a list of lookup dictionaries, and a request dictionary.
Functions return fresh output lists and do not mutate inputs. This package re-exports
the tested implementation from `published.a01_r04` (transitively using
`published.a01_r03`); it adds no independent transformation behavior.

`clean` strips/lowercases non-null regions and fills missing units with request
`fill` (`zero`, `mean`, or `median`; all-missing -> 0). `revenue` also appends
`revenue_cents`, null when units or price are missing. `group` aggregates valid
revenue by normalized region; `monthly` aggregates by month and normalized region,
dropping missing keys. Both accept `agg` (`sum`, `mean`, `count`) and sort keys;
empty sums/counts are zero and empty means null. `lookup` adds
`revenue_cents_per_target` from exact normalized-region lookup, null for unknown
regions, absent/zero targets or missing revenue. `window` adds the mean of available
revenue over trailing request `window` rows (including current).

Example: `clean([{'region': ' NW ', 'units': None}], [], {'fill': 'zero'})`
returns `[{'region': 'nw', 'units': 0}]`.

Limitations: expects the documented row schema and valid fill/aggregation/window
choices; no extra validation or behavior beyond the dependency is provided.
