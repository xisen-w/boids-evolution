# Table services

Pure-Python adapters for the six service families. Public functions are
`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`.
Each accepts a list of row dictionaries, a lookup-row list, and a request
mapping, and returns new dictionaries without mutating the inputs. Requests
use `fill` (`zero`, `mean`, `median`; default `zero`), `agg` (`sum`, `mean`,
`count`; default `sum`), or `window` (2, 3, or 4) as applicable.

Example: `revenue([{'region':' WEST ', 'units':2, 'price_cents':125}], [], {'fill':'zero'})`
returns `[{'region':'west', 'units':2, 'price_cents':125, 'revenue_cents':250}]`.
`clean` preserves original keys and order; revenue-derived services append
`revenue_cents`. Group services return only grouping keys and aggregate.
Lookup uses normalized region keys on both row and lookup records. Invalid
fill/aggregation/window settings raise `ValueError`. Input values are expected
to follow the service schema; date grouping uses the first seven date characters.
