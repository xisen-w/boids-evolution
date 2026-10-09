# Tabular service functions

Native Python implementation; no third-party dependencies. Public root functions `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)` each return a new list of dictionaries and do not mutate inputs. Rows use the schema described by the service contract. `lookup` accepts the lookup-row list as its second argument (the function is named `lookup`, so this argument is locally shadowed only within its body).

- `clean`: normalizes region using strip/lower and fills missing units by `request['fill']` (`zero`, `mean`, or `median`; defaults to zero).
- `revenue`: same unit filling and normalization, plus revenue cents.
- `group`: revenue transform then group by nonmissing region using `request['agg']` (`sum`, `mean`, `count`; defaults to sum).
- `monthly`: same aggregation grouped by month and region.
- `lookup`: adds revenue per exact normalized region target; target and manager columns are not added.
- `window`: adds trailing row-window mean; `request['window']` defaults to 2.

Example: `revenue([{'region':' West ', 'units':2, 'price_cents':150}], [], {'fill':'zero'})` returns a row with normalized region `west` and `revenue_cents` 300. The input schema's date is expected to be an ISO date string for monthly grouping. Aggregate count excludes missing revenues. Empty sum/count groups yield zero; empty means yield `None`.
