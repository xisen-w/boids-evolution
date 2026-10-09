# Tabular service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup_service(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns the complete service output described by its family. `rows` and `lookup` are lists of dictionaries; request supports `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`), and `window` (2, 3, or 4). Inputs are not mutated.

Example: `revenue([{'units': 2, 'price_cents': 150}], [], {'fill': 'zero'})` returns `[{'units': 2, 'price_cents': 150, 'revenue_cents': 300}]`.

Implementations delegate to the received, dependency-declared `published.a00_r02` package. Inputs follow the service schema; no validation of malformed requests is promised.
