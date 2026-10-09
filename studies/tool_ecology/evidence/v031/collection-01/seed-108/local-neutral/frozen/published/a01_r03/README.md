# Row service adapters

This package re-exports the verified `a01_r02` Python row-table service API.

Each function accepts `(rows, lookup, request)` and returns a fresh result:

- `clean_service`: normalize nonmissing regions and fill missing units.
- `revenue_service`: fill units and append `revenue_cents`.
- `group_service`: normalized-region revenue aggregation.
- `monthly_service`: monthly and region revenue aggregation.
- `lookup_service`: add revenue per region target.
- `window_service`: add trailing-row mean revenue.

Example: `revenue_service(rows, [], {'fill': 'median'})`. Fill modes are
`zero`, `mean`, and `median`; aggregation modes are `sum`, `mean`, and
`count`. Window width is supplied by `request['window']`. Input objects are
not modified. Aggregation excludes missing revenue; groups omit missing keys.
These functions expect the documented list-of-dictionaries inputs and valid
request modes.
