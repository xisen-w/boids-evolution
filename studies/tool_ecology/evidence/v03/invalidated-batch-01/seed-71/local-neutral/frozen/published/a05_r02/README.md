# Row-table services

Pure Python, no third-party dependencies. Public functions all have signature
`function(rows, lookup, request)` and return new row dictionaries/lists without
mutating inputs. Rows retain input order for row services. Supported fill modes:
`zero`, `mean`, and `median` (even-sized median averages central values; all
missing fills with zero). Supported aggregation modes are `sum`, `mean`, `count`.

* `clean(rows, lookup, request)`: strips/lowercases region and fills units.
* `revenue(...)`: fills units and adds `revenue_cents`; region and all other
  original fields are preserved. Revenue is `None` if units or price is missing.
* `group(...)`: normalized region groups, nonmissing revenue aggregation.
* `monthly(...)`: normalized region and YYYY-MM groups; missing date/region keys
  are excluded.
* `lookup(...)`: normalized row region and `revenue_cents_per_target`, using
  lookup region keys as supplied; missing/zero targets give `None`.
* `window(...)`: adds trailing ROWS-window mean (window 2, 3, or 4), ignoring
  missing revenue values within each frame.

Example: `revenue([{'units': 2, 'price_cents': 40}], [], {'fill':'zero'})`
returns `[{'units': 2, 'price_cents': 40, 'revenue_cents': 80}]`.
