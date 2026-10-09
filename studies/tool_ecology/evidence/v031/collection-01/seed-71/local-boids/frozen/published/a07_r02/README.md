# Tabular services

Dependency-free native Python adapters. Every function accepts `(rows, lookup, request)` and returns fresh dictionaries without mutating inputs. Example: `revenue([{'region':' West ','units':2,'price_cents':50}], [], {'fill':'zero'})` returns the original region and appends `revenue_cents: 100`.

* `clean`: strip/lower string regions; fill missing units using `request['fill']` (`zero`, `mean`, `median`; all missing -> 0); preserve columns/order.
* `revenue`: fill missing units and append `revenue_cents` (None if units or price is missing); does not normalize region.
* `group`: normalized region and revenue; drops missing regions; output grouped records by region with requested sum/mean/count of nonmissing revenue.
* `monthly`: like group, grouping by date month and region and dropping missing keys.
* `lookup`: normalized region/revenue plus per-target revenue from exact normalized region match; unknown, missing/zero target or missing revenue gives None.
* `window`: revenue plus rolling mean over trailing `request['window']` rows including current, ignoring missing revenue (not missing rows); preserves original region.

Aggregates are selected with `request['agg']`; windows accept 2, 3, or 4. Input tables are lists of mappings with the documented fields. Invalid fill/aggregate/window values raise ValueError. No target/manager fields are added.
