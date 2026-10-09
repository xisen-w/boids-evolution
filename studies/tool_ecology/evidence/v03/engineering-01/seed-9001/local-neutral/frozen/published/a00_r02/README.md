# Tabular services

Dependency-free APIs: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Matching `serve_*` aliases are publication adapters. Inputs are lists of row dictionaries; all return fresh dictionaries and do not mutate arguments. `lookup` argument is the lookup-table iterable (despite sharing its function's name).

`clean` strips/lowercases string regions and fills null units; `revenue` fills units and appends `revenue_cents`, without changing region. Fill mode is request `fill`: zero/mean/median (default zero); all-null units fill with zero. Revenue is null if price is null. Group and monthly normalize region and aggregate non-null revenue by region or `(date[:7], region)`, dropping null group keys. `agg` is sum/mean/count (default sum); empty aggregates yield 0 for sum/count and null for mean. Lookup normalizes regions and appends `revenue_cents_per_target`; unknown/null/zero targets yield null. Window appends the mean of non-null revenues in trailing rows including current; `window` is 2, 3, or 4 (default 2).

Example: `revenue([{'units': None, 'price_cents': 5}], [], {'fill':'zero'})` returns `[{'units': 0, 'price_cents': 5, 'revenue_cents': 0}]`.

Rows are expected to contain ordinary numeric values or `None`; unsupported fill/aggregation/window options raise `ValueError`. Dates are sliced to their first seven characters. No external dependencies.
