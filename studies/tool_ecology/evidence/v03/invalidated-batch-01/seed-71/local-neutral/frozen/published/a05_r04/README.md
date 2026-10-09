# Row table transformations

Native Python implementation of six non-mutating services. Public functions all have signature `service(rows, lookup, request)` and return a new list of row dictionaries (or grouped dictionaries). The `lookup` argument is unused except by `lookup` service.

- `clean`: normalize region with strip/lower and fill missing units.
- `revenue`: fill units and append `revenue_cents` (None if price is missing).
- `group`: aggregate nonmissing revenue by normalized nonmissing region.
- `monthly`: aggregate by nonmissing `date[:7]` and normalized region.
- `lookup`: append `revenue_cents_per_target` from exact normalized-region matching; does not append lookup fields.
- `window`: append mean revenue over trailing ROWS including current.

Example: `revenue([{'units': 2, 'price_cents': 50}], [], {'fill':'zero'})` yields `[{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]`.

`request.fill` is `zero`, `mean`, or `median` (all-missing fills with zero; even medians average central values). Grouping requires `request.agg` of `sum`, `mean`, or `count`; count excludes missing revenue. Window requires width 2, 3, or 4. Grouped empty means are None; sum/count empty buckets are zero. Inputs are not modified. Rows are expected to follow the documented row-table schema; malformed rows and invalid request values are not supported.
