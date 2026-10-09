# Tabular service adapters

Native Python implementation; no external dependencies. Import from `candidate` (or the published package root).

Each public callable takes `(rows, lookup, request)` and returns fresh dictionaries without mutating inputs:

* `clean(rows, lookup, request)`: normalizes string `region` values with strip/lower and fills missing `units` using `request['fill']` (`zero`, `mean`, or `median`; default `zero`).
* `revenue(...)`: clean output with `revenue_cents` appended (`units * price_cents`, or `None` if either is missing).
* `group(...)`: groups nonmissing normalized region keys and appends no row-level fields; returns `region` and `<agg>_revenue_cents` records.
* `monthly(...)`: like `group`, grouped by `date[:7]` and region; output keys are `month`, `region`, and `<agg>_revenue_cents`.
* `lookup(...)`: revenue output plus `revenue_cents_per_target`, using exact normalized region matching; missing/zero targets produce `None`.
* `window(...)`: revenue output plus trailing-row (including current row) `roll_revenue_cents` means.

Grouped services use `request['agg']` (`sum`, `mean`, or `count`; default `sum`); count excludes missing revenues. Empty sum/count groups are represented as zero, and empty means as `None`. Window size is `request['window']` (2, 3, or 4). Example: `revenue([{'region':' West ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})` returns a row with region `west` and revenue 100. Other input columns are preserved in their original order, with derived columns appended. Group results are lexically sorted by stringified keys. Inputs are expected to be the documented row dictionaries; invalid fill/aggregate/window options raise `ValueError`.
