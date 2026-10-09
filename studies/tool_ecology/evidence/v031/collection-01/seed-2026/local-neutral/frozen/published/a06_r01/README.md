# Tabular service helpers

All APIs are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)` in
`candidate`. Inputs are lists of mappings; inputs are not mutated. Row services
copy each row and retain its columns/order, appending derived fields. Region
strings are stripped and lowercased. Missing units use `request['fill']`
(`zero`, `mean`, or `median`; default `zero`), with all-missing resolving to 0.

`revenue` appends `revenue_cents`, null if units or price are null. `group`
returns rows `{region, <agg>_revenue_cents}`, excluding null regions.
`monthly` returns `{month, region, <agg>_revenue_cents}`, excluding null month
or region; month is the first seven characters of date. Both grouped APIs use
`request['agg']` (`sum`, `mean`, `count`; default `sum`), omit null revenues
from aggregation and sort keys lexically. Empty sum/count groups resolve to 0;
empty means to null. `lookup` appends `revenue_cents_per_target`, matching the
normalized region to lookup region and yielding null for absent/null/zero
values. `window` appends the trailing `request['window']`-row mean of non-null
revenues (including current row), default window 2; empty windows yield null.

Example: `revenue([{'region':' NW ', 'units':2, 'price_cents':50}], [],
{'fill':'zero'})` returns a row with normalized region `nw` and revenue 100.
The APIs expect mapping-like rows, a sequence of lookup mappings, and valid
fill/aggregation names and positive window widths.
