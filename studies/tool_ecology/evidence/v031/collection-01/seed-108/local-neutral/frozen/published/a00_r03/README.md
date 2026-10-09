# Row-table services

Public functions accept `(rows, lookup, request)` and return a new list of row dictionaries (or grouped result dictionaries), without modifying inputs. This package delegates to `published.a00_r02`; that dependency must accompany this package.

* `clean(rows, lookup, request)`: normalize regions and fill missing units according to `request['fill']` (`zero`, `mean`, or `median`).
* `revenue(...)`: clean units and add `revenue_cents`.
* `group(...)`: normalize and derive revenue, aggregate by region using `request['agg']` (`sum`, `mean`, `count`).
* `monthly(...)`: aggregate by month and region.
* `lookup_service(...)`: add revenue per exact-region target; lookup rows have `region` and `target` fields.
* `window(...)`: add trailing row-window revenue mean using `request['window']`.

For example: `from candidate import revenue; result = revenue(rows, [], {'fill': 'zero'})`. Missing values and empty input follow the service contract; aggregations sort keys. Lookup does not add target or manager columns. No additional dependencies are required beyond the declared published package.
