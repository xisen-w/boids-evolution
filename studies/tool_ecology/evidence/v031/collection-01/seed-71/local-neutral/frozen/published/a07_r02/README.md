# Native tabular services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` from this package. Every function has the service-adapter signature `(rows, lookup, request)` and returns a new list of dictionaries without mutating inputs. Rows retain their key order; appended derived keys follow the existing keys.

* `clean(rows, lookup, request)`: normalize string regions with strip/lower and fill absent (`None`) units using `request['fill']` (`zero`, `mean`, or `median`).
* `revenue(...)`: fill units and append `revenue_cents`, null when units or price is null.
* `group(...)`: normalize regions and group by region; `request['agg']` is `sum`, `mean`, or `count` over non-null revenue.
* `monthly(...)`: like group, with an additional `YYYY-MM` key from date.
* `lookup(...)`: fill units, normalize each row region, append revenue and `revenue_cents_per_target` based on exact normalized region matching. Missing/zero targets yield null.
* `window(...)`: fill units and append trailing `request['window']` ROWS mean (`2`, `3`, or `4`) of available revenues.

Example: `revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})` returns `[{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]`.

All-missing unit values fill as zero. Median uses the conventional midpoint for even populations. Grouping drops null keys and mean of an empty valid-value set is null. This API expects list-of-dict inputs and the documented request values; it does not validate schemas beyond required request options.
