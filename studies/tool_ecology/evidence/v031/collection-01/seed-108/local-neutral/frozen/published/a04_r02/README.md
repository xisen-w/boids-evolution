# Tabular services

Pure Python, non-mutating row-dictionary adapters. Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. `request.fill` accepts `zero`, `mean`, `median` (default zero); aggregate accepts `sum`, `mean`, `count` (default sum); window accepts 2, 3, or 4. Clean normalizes region and fills units only; revenue also adds revenue_cents; group/monthly aggregate; lookup adds per-target revenue; window adds trailing row-window mean.

Example: `revenue([{'region':' EAST ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})` returns the row with region `east` and `revenue_cents: 100`.

Inputs are lists of mappings; output mappings are shallow copies. Missing means `None`. Lookup keys are normalized as region strings. Grouping drops missing keys. No schema validation beyond supported request options.
