# rowservices

Dependency-free functions over lists of dictionaries. Public service signatures are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup_service(rows, lookup, request)`, and `window(rows, lookup, request)`. `lookup` is unused except for the lookup service. Requests use `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`) and `window` (row count).

Example: `revenue([{'region':' West ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})` returns a copied row with normalized region `west` and revenue 100. Clean retains supplied columns without adding revenue; other row services preserve columns and append derived fields. Group/monthly return aggregate-only records. Missing group keys are dropped; missing revenues are excluded from aggregates. Inputs are not modified. Invalid option strings fall back to zero fill or sum aggregation; dates are expected in ISO form.
