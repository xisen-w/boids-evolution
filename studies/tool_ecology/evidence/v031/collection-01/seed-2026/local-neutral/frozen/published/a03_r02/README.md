# Regional row-table services

Dependency-free Python functions; all adapters accept `(rows, lookup, request)` and return new row dictionaries without mutating inputs.

- `clean(rows, lookup, request)`: normalize region with strip/lower and fill missing units.
- `revenue(rows, lookup, request)`: fill missing units and append revenue_cents; preserves region as supplied.
- `group(...)`, `monthly(...)`: normalized regional revenue aggregations.
- `lookup(...)`: normalized revenue and revenue_cents_per_target from normalized exact region keys.
- `window(...)`: revenue plus trailing ROWS mean.

`request.fill` is zero (default), mean, or median; all-missing units become zero. `request.agg` is sum (default), mean, or count. `request.window` is 2 (default), 3, or 4. Aggregations ignore missing revenue; empty sums/counts are zero and empty means are None. Example: `group(rows, [], {'fill':'median','agg':'sum'})`.
