# Row services

Dependency-free transformations on lists of row dictionaries. Public adapters `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)` return new rows and do not mutate arguments. `clean` normalizes string region values (strip/lower) and fills missing units. Fill mode `zero`, `mean`, or `median` is selected with `request['fill']` (default `zero`); all-missing uses zero. `revenue` fills units and appends `revenue_cents`; it does not normalize region. Missing units or price produce None revenue.

`group` and `monthly` normalize regions and group by nonmissing keys. `monthly` uses date's first seven characters. Set `request['agg']` to `sum`, `mean`, or `count` (default sum); means/counts ignore missing revenue. Outputs sort by stringified keys. `lookup` normalizes region and lookup keys and appends `revenue_cents_per_target`; absent/zero targets yield None. `window` appends the trailing-row mean `roll_revenue_cents`; set `request['window']` to 2, 3, or 4 (default 2).

Example: `revenue([{'units': 2, 'price_cents': 50}], [], {})` gives `[{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]`. Inputs are expected to have numeric operands and string-or-None regions; invalid fill/aggregation/window values raise ValueError.
