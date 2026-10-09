# a03_r06
Native, dependency-free adapters for all six table services. Public API: `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)`. Inputs are lists of row dictionaries; functions return new dictionaries and do not mutate inputs.

`request.fill` is `zero`, `mean`, or `median`; `request.agg` is `sum`, `mean`, or `count`; `request.window` is trailing ROWS size 2, 3, or 4. Example: `group(rows, [], {'fill':'mean','agg':'sum'})` returns normalized region groups with `sum_revenue_cents`. Missing revenue is excluded from aggregates; empty sum/count are zero and empty mean is None. `lookup` adds per-target revenue using exact keys in lookup rows. No third-party dependencies.
