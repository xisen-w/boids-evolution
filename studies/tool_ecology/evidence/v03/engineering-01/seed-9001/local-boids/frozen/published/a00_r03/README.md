# Row services

The package exports `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup_service(rows, lookup, request)`, and `window(rows, lookup, request)`.
Each returns the full family-specific output described below; inputs are row dictionaries,
lookup dictionaries, and a request dictionary. The lookup family is named `lookup_service`
to avoid shadowing the lookup argument.

Example: `revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})`
returns `[{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]`.

Services preserve input data and row order where applicable; clean normalizes region and
fills missing units, revenue derives cents, group/monthly aggregate, lookup computes the
per-target ratio, and window computes trailing-row mean. Parameters support zero/mean/median
fill, sum/mean/count aggregation, and windows 2/3/4. Exact validation and edge handling
are those of the declared dependency `a01_r02`. No additional behaviors are implemented
locally.
