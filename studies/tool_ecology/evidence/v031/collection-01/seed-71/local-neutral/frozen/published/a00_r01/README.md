# table_services

Native Python implementations of six table services. Public adapters all have signature `(rows, lookup, request)` and return new lists/dicts without mutating inputs: `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`.

`clean` normalizes string regions via strip/lower and fills null units using `request['fill']` (`zero`, `mean`, or `median`; all missing becomes zero). `revenue` does the same filling and adds `revenue_cents`, null when price or units is null. `group` and `monthly` aggregate non-null revenue (sum/mean/count selected by `request['agg']`), dropping null group keys. `lookup` adds `revenue_cents_per_target` using normalized exact region keys. `window` adds trailing-row mean `roll_revenue_cents`; `request['window']` is row width including current row.

Example: `from candidate import revenue; revenue([{'units': 2, 'price_cents': 5}], [], {'fill':'zero'})` returns `[{'units': 2, 'price_cents': 5, 'revenue_cents': 10}]`.

Inputs are expected to be row dictionaries. The services preserve existing field values and row order except grouped outputs, which are sorted by stringified keys. Lookup targets are keyed by normalized region. Aggregation modes/fill modes should use the values specified above.
