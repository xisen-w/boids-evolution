# Tabular services

Native Python APIs: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. Each returns new row dictionaries and does not mutate inputs. The lookup argument is ignored except by `lookup`.

`request.fill` supports `zero`, `mean`, and `median` (default `zero`; all missing fills with 0). Aggregation uses `request.agg` (`sum`, `mean`, `count`; default `sum`). Window requires 2, 3, or 4 rows. Group/monthly drop missing keys and sort stringified keys. Revenue/window preserve region values; clean/group/monthly/lookup normalize strings by stripping and lowercasing.

Example: `revenue([{'region':' East ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})` gives `region: ' East '` and `revenue_cents: 100`.

Missing values are represented by `None`. These APIs expect row mappings and supported request options; they do not perform schema validation.
