# Tabular service functions

Native Python implementations; no external dependencies. All adapters accept `(rows, lookup, request)`. Input rows and request/lookup are not mutated; output dictionaries are shallow copies and retain original field order, with derived columns appended. Missing numeric values are `None`.

Public adapters: `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.

- `clean`: normalizes non-null region strings with strip/lower and fills units per `request['fill']` (`zero`, `mean`, `median`; default `zero`). Example: `clean([{'region':' WEST ','units':None}], [], {'fill':'zero'})` returns `[{'region':'west','units':0}]`.
- `revenue`: applies the units fill then appends `revenue_cents` (`units * price_cents`, or `None` if price is missing).
- `group`: normalizes region, derives revenue and returns one row per non-null region, aggregated by `request['agg']` (`sum`, `mean`, `count`; default `sum`).
- `monthly`: same aggregation grouped by month (`date[:7]`) and region; rows missing either key are dropped.
- `lookup`: appends `revenue_cents_per_target`, using exact normalized region match; missing/zero target or missing revenue gives `None`. Other lookup fields are not emitted.
- `window`: appends the trailing-row mean `roll_revenue_cents`; `request['window']` is 2, 3, or 4 (default 2), and missing revenues are excluded from the mean but still occupy rows.

Aggregations count only nonmissing revenues; empty means are `None`, while empty sums/counts are zero. Unsupported fill, aggregation, or window values raise `ValueError`. Inputs are expected to be lists of mappings with the documented service fields.
