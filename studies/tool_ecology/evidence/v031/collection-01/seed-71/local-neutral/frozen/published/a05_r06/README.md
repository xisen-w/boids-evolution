# Row transforms

Native Python, no dependencies. Public service adapters accept `(rows, lookup, request)` and return new row dictionaries (inputs are not mutated).

* `clean`: normalized lowercase/stripped region and units filled using `request['fill']` (`zero`, `mean`, `median`; default zero). Keeps original columns and order.
* `revenue`: same region/unit normalization and adds `revenue_cents`, null if units or price is null.
* `group`: normalized revenue grouped by non-null region; `request['agg']` is `sum`, `mean`, or `count` (default sum). Missing revenue is excluded; empty sum/count are 0 and empty mean is null.
* `monthly`: same aggregation grouped by non-null month (`date[:7]`) and region.
* `lookup`: adds revenue per exact normalized region target; unknown/null/zero target or null revenue gives null. Lookup manager is ignored.
* `window`: adds trailing ROWS mean over `request['window']` rows (default 2), excluding null revenues; all-null window gives null.

Example: `revenue([{'region':' West ','units':2,'price_cents':50}], [], {'fill':'zero'})` returns a row with region `west` and revenue 100. Group outputs sort by stringified keys. Existing input column order is retained and derived columns appended; no external packages are used.
