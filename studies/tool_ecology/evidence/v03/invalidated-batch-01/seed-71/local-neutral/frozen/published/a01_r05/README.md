# Tabular service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`.
Each takes a list of row dictionaries, lookup rows (ignored except by the lookup
service), and a request dictionary and returns fresh output dictionaries without
mutating its inputs. This package reuses `published.a01_r04`.

Request parameters: `fill` is `zero`, `mean`, or `median` (default `zero`);
`agg` is `sum`, `mean`, or `count` (default `sum`); `window` is a positive
integer row width (default 2). Regions are stripped and lowercased where
specified. Derived revenue is units times price, or None if price is missing.

Example:
```python
from candidate import clean
clean([{'region':' EAST ', 'units':None}], [], {'fill':'zero'})
# [{'region': 'east', 'units': 0}]
```
Limitations: follows the input schema and semantics documented above; invalid
fill/aggregation/window parameters raise ValueError (invalid width also rejects
non-integers). Lookup is keyed by normalized exact region.
