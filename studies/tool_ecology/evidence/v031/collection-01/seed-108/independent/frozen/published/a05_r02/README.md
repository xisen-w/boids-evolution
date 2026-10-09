# Tabular transformations

Native Python implementations of six row-table services. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. Each returns new dictionaries and does not mutate arguments. Rows are lists of dictionaries.

`fill` supports `zero`, `mean`, and `median` (default `zero`); missing units are filled across the input rows, with all-missing values filled as zero. `agg` supports `sum`, `mean`, and `count` (default `sum`). `window` requires 2, 3, or 4. `clean`, `group`, `monthly`, and `lookup` normalize region strings by strip/lower; `revenue` and `window` leave region unchanged. Revenue is `units * price_cents`, or None when price is missing. Grouping drops missing keys and aggregates nonmissing revenue; monthly uses `date[:7]`. Lookup matches normalized region keys and yields None for missing/zero targets or missing revenue. Window is the trailing-row mean over nonmissing revenue.

Example: `revenue([{'region':' West ','units':2,'price_cents':5}], [], {'fill':'zero'})` returns `[{'region':' West ','units':2,'price_cents':5,'revenue_cents':10}]`.

Limitations: dates are treated as ISO-like strings; malformed types/options raise Python exceptions; grouped region values are expected to be hashable.
