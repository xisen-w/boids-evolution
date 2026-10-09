# Row services

Dependency-free Python adapters for the six row-table service families. Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)` in `candidate`. Inputs are lists of dictionaries; inputs are not mutated. Request supports `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`), and `window` (2, 3, or 4) as appropriate.

Example: `revenue([{'units': None, 'price_cents': 25}], [], {'fill':'zero'})` returns `[{'units': 0, 'price_cents': 25, 'revenue_cents': 0}]`. Clean normalizes string regions with strip/lower; the revenue and window services retain region values. Group/monthly/lookup normalize regions as defined by their services. Aggregations omit missing group keys and ignore missing revenue; empty sums/counts are zero and empty means are `None`.

Limitations: row fields are expected to be ordinary Python numbers/strings/None as specified; malformed dates and unsupported request options are not specially handled.
