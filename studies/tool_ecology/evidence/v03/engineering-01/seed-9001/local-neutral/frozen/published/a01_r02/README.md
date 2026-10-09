# Native table services

Dependency-free list-of-dictionary adapters. Public functions `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)` return new row dictionaries/lists and do not mutate arguments. `lookup` argument is lookup-table rows for that service.

`clean` normalizes non-null region strings and fills missing units. `revenue` fills units and derives `revenue_cents`. `group` and `monthly` group normalized rows and aggregate nonmissing revenue. `lookup` adds revenue per target using normalized region keys on both sides; the lookup manager and target are not added to output. `window` calculates a trailing ROWS mean. Request keys: fill (`zero`, `mean`, `median`), agg (`sum`, `mean`, `count`), window (width). Example: `group(rows, [], {'fill':'mean','agg':'sum'})`.

Missing prices produce missing revenue; all-missing units fill with zero. Aggregations omit missing revenue; empty mean is None and empty sum/count are zero. Null group keys are dropped.
