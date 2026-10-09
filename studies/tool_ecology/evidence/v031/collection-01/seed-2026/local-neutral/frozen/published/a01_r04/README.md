# Row-table service adapters

Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts
rows and lookup rows as lists of dictionaries and a request dictionary; each
returns a fresh list of dictionaries without mutating inputs.

* `clean` normalizes non-null regions with strip/lower and fills missing units
  according to `request['fill']`: `zero`, `mean`, or `median` (all missing -> 0).
* `revenue` applies that fill and appends `revenue_cents` (null if units or price
  is missing).
* `group` aggregates non-null revenue by normalized region; `monthly` groups by
  `date[:7]` and region. Both drop missing keys and accept `agg` of `sum`,
  `mean`, or `count`, returning sorted aggregate rows.
* `lookup` adds `revenue_cents_per_target` using exact normalized region lookup;
  missing/unknown/zero targets or missing revenue produce null.
* `window` adds `roll_revenue_cents`, the non-null revenue mean over trailing
  `request['window']` rows including current.

Example: `clean([{'region': ' NW ', 'units': None}], [], {'fill':'zero'})`
returns `[{'region':'nw', 'units':0}]`. Empty sum/count aggregates are zero;
empty means are null. Inputs should follow the documented service schema and
valid request choices. Implementations are re-exported from the verified
`published.a01_r03` package.
