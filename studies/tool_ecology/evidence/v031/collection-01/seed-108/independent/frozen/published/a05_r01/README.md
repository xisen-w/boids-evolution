# Tabular transformations

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup_rows, request)`. Import from `candidate` (or this package when published). Each accepts a list of row dictionaries, lookup dictionaries (unused except by `lookup`), and request dictionary; inputs are not mutated. `fill` is `zero`, `mean`, or `median` (default `zero`); all-missing units fill with zero. `agg` is `sum`, `mean`, or `count` (default `sum`). `window` requires 2, 3, or 4.

Region strings are stripped and lowercased. Revenue outputs append `revenue_cents`; grouping emits sorted aggregate rows; monthly grouping uses the first seven date characters. Lookup adds `revenue_cents_per_target`; lookup region keys receive the same strip/lower normalization, with exact normalized-key matching. Window adds a trailing-row mean. Example: `revenue([{'region':' West ','units':2,'price_cents':5}], [], {'fill':'zero'})` returns `[{...,'region':'west','units':2,'revenue_cents':10}]` (with all original keys retained).

Limitations: dates are treated as ISO-like strings and month extraction is lexical; malformed input types and invalid options raise normal Python exceptions. Region keys are assumed hashable for grouped services.
