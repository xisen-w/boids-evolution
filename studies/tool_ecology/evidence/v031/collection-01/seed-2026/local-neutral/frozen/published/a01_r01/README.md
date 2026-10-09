# table_services

Native Python implementations of six table services. Public functions all accept `(rows, lookup, request)` and return new dictionaries without mutating arguments:

- `clean(rows, lookup, request)`: strip/lower non-null regions and fill null units using `request['fill']` (`zero`, `mean`, `median`; defaults to zero; all-missing becomes zero). Retains all fields and row order.
- `revenue(...)`: fill units and append `revenue_cents` (`units * price_cents`, or null if either is null); otherwise retains input region spelling and row order.
- `group(...)`: normalized region plus revenue, grouped by non-null region; `request['agg']` supports `sum`, `mean`, `count`; sorted by stringified region. Empty sum/count are zero and empty mean null.
- `monthly(...)`: as group with month from first seven date characters; groups on month and region, sorted by those keys.
- `lookup(...)`: normalized region and revenue, then `revenue_cents_per_target` using the exact normalized region key in lookup; absent/null/zero target or null revenue yields null. Does not append lookup fields.
- `window(...)`: revenue plus mean of non-null revenues in the trailing `request['window']` rows, including current; null if none.

Example: `group([{'region':' NW ', 'units':2, 'price_cents':5}], [], {'fill':'zero','agg':'sum'})` returns `[{'region':'nw','sum_revenue_cents':10}]`.

Inputs are expected to be lists of mappings with the documented fields. Aggregation and window options are expected to be from the listed choices; no external dependencies.
