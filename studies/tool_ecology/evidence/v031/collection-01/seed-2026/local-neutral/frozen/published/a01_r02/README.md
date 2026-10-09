# Row table services

Native Python adapters for six row-table service families. Every public function accepts `(rows, lookup, request)`, returns fresh row dictionaries, and does not mutate arguments.

- `clean`: preserves precisely the input columns/order of rows; strips and lowercases non-null region values and fills missing `units` according to `request['fill']` (`zero`, `mean`, `median`; all-missing becomes zero).
- `revenue`: fills units and adds `revenue_cents` (null when units or price is null); other input fields retained.
- `group`: normalized region and derived revenue, grouped by non-null region; `request['agg']` is sum/mean/count; sorted by stringified region.
- `monthly`: as group, grouping by month (`date[:7]`) and region; rows with either missing key dropped and output sorted by stringified keys.
- `lookup`: normalized region and revenue plus `revenue_cents_per_target`; exact normalized region lookup, null for unknown/missing/zero target or null revenue.
- `window`: revenue plus mean non-null revenue over trailing `request['window']` rows including current.

Aggregates count non-null revenues; empty sum/count are zero, empty mean is null. Example: `clean([{'region':' NW ', 'units':None}], [], {'fill':'zero'})` returns `[{'region':'nw','units':0}]`. The five non-clean functions are reused from `published.a01_r01`; choices are expected to be valid service values.
