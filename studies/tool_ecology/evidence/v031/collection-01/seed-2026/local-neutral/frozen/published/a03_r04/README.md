# Regional row-table services

Dependency-free native Python implementations. Public adapters accept `(rows, lookup, request)` and return fresh dictionaries; inputs are not mutated. Supported functions are `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.

- `clean`: strip/lower region and fill missing units.
- `revenue`: fill missing units and append `revenue_cents`, retaining region unchanged.
- `group`: normalized region and revenue, aggregate by region (drop missing keys).
- `monthly`: normalized region/revenue, add date prefix month, aggregate by month and region (drop missing keys).
- `lookup`: normalized region/revenue and append revenue per exact normalized region target; missing/unknown region, target, zero target, or revenue produces None. Does not append lookup metadata.
- `window`: revenue plus trailing ROWS mean including current row; preserves region text.

`request` supports `fill`=`zero`/`mean`/`median` (default zero; all missing becomes zero), `agg`=`sum`/`mean`/`count` (default sum; missing revenues ignored; empty sum/count zero and empty mean None), and `window`=2/3/4 (default 2). Median for even inputs is the central-value average. Example: `group(rows, [], {'fill': 'median', 'agg': 'sum'})`. Tables may be empty.
