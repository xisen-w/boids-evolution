# Table services

Dependency-free Python implementations. Each public function has the same API:
`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Inputs are lists of mappings; results are newly allocated dictionaries and inputs are not modified.

`request.fill` is `zero`, `mean`, or `median`; missing units are filled using the nonmissing units across the input (all missing gives zero). `request.agg` is `sum`, `mean`, or `count`. `request.window` is 2, 3, or 4 rows. Regions are stripped and lowercased. Revenue is units times price, or `None` when price is missing. Aggregations drop missing keys and count nonmissing revenues. Lookup matches normalized region keys and returns revenue divided by target, or `None` for unknown/zero/missing targets. Rolling mean includes current row and preceding rows in its fixed-size row window.

Example: `revenue([{'region':' West ', 'units':None, 'price_cents':5}], [], {'fill':'zero'})` returns a row with normalized region `west`, units `0`, and revenue_cents `0`.

Limitations: rows and lookup entries are expected to be mappings with the fields defined by the service contract; malformed values and unsupported request parameters raise ordinary Python errors/ValueError.
