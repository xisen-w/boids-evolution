# a01_r05

Pure-Python row transformations; all public adapters have signature `(rows, lookup, request)` and return new dictionaries without mutating arguments. Rows retain their original keys and order; derived columns are appended. The root functions `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` implement the six service families. `request.fill` accepts `zero`, `mean`, or `median` (all-missing -> 0); aggregations accept `sum`, `mean`, or `count`; window accepts 2, 3, or 4. Region strings are stripped and lowercased. Group outputs omit missing keys and sort by stringified keys.

Example: `revenue([{'region':' East ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})` returns a row with region `east` and `revenue_cents` 100.

Limitations: inputs follow the documented service schema (numeric units/prices and string-or-None regions); duplicate lookup regions use the last entry.
