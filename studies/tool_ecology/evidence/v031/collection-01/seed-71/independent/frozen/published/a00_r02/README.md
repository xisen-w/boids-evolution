# Tabular service adapters

Pure native-Python functions, no dependencies. Public call signature for every adapter is `(rows, lookup, request)`; inputs are not mutated. Rows are shallow-copied and retain their original key order, with derived keys appended. Null values are represented by `None`.

Adapters: `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`.

- `clean(rows, lookup, request)` strips/lowercases non-null regions and fills missing units using `request['fill']`: `zero`, `mean`, or `median` (default `zero`; all missing -> 0).
- `revenue(...)` fills units and adds `revenue_cents = units * price_cents`, or `None` if either is missing.
- `group(...)` groups by normalized nonmissing region and aggregates nonmissing revenues using `request['agg']` (`sum`, `mean`, `count`; default `sum`). Output is sorted by stringified region.
- `monthly(...)` groups by nonmissing `(date[:7], normalized region)`, sorted by stringified keys.
- `lookup(...)` adds `revenue_cents_per_target`, looking up the row's normalized region by exact key in lookup records. Unknown keys, missing/zero targets, and missing revenues yield `None`. Lookup keys are not themselves normalized.
- `window(...)` adds `roll_revenue_cents`, the mean of nonmissing revenues among the trailing `request['window']` rows, including current; allowed widths are 2, 3, 4 (default 2). Missing values occupy window positions.

Aggregate columns are named `<agg>_revenue_cents`. Empty sum/count are zero; empty mean is `None`. Unsupported fill/aggregation/window raises `ValueError`.

Example: `revenue([{'units': 2, 'price_cents': 15}], [], {})` returns `[{'units': 2, 'price_cents': 15, 'revenue_cents': 30}]`.
