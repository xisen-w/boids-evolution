# Row table services

Dependency-free public adapters (the implementation is delegated to the received,
verified `published.a00_r04` package). All functions accept
`(rows, lookup, request)` where rows/lookup are lists of dictionaries and request
is a dictionary, and return new dictionaries without modifying inputs.

* `clean(rows, lookup, request)`: normalize non-null regions with strip/lower and
  fill null units using `request['fill']` (`zero`, `mean`, or `median`; default
  zero). Preserves row and column order.
* `revenue(...)`: fill units, then append `revenue_cents` (null when units or
  price is null).
* `group(...)`: normalized-region revenue aggregation. `request['agg']` is
  `sum`, `mean`, or `count` (default sum); missing regions are omitted.
* `monthly(...)`: aggregate by date prefix `YYYY-MM` and normalized region;
  rows with either missing key are omitted. Uses the same `agg` choices.
* `lookup_service(...)`: append `revenue_cents_per_target`; uses lookup region
  keys, and returns null for absent/null/zero target or null revenue.
* `window(...)`: append trailing-rows mean `roll_revenue_cents`; `request['window']`
  must be 2, 3, or 4. Null revenues are skipped within the row window.

Example: `clean([{'region':' West ', 'units':None}], [], {'fill':'zero'})`
returns `[{'region':'west', 'units':0}]`. Aggregates return only their documented
key and aggregate fields; sum/count empty-value groups are zero and mean is null.
