# Row-table services

Native Python adapters for six tabular transformations. Every public service accepts `(rows, lookup, request)` and returns a fresh list of dictionaries; inputs are not modified. This package delegates to `published.a00_r02`, which must be installed alongside it.

- `clean(rows, lookup, request)`: strip/lowercase regions and fill missing units using `request['fill']` (`zero`, `mean`, or `median`; all-missing becomes zero). Preserves columns and order.
- `revenue(...)`: same cleaning, plus `revenue_cents` (None when units or price is missing).
- `group(...)`: groups nonmissing normalized regions, aggregating nonmissing revenue using `request['agg']` (`sum`, `mean`, `count`).
- `monthly(...)`: groups by month (`date[:7]`) and region, dropping missing keys, with the requested aggregation.
- `lookup_service(...)`: adds `revenue_cents_per_target` based on exact normalized region matching. Unknown region, absent/zero target or missing revenue yields None; lookup metadata is not added.
- `window(...)`: adds trailing `request['window']`-row mean of nonmissing revenue, including current row; missing values do not extend the row window.

Example: `from candidate import revenue; out = revenue(rows, [], {'fill': 'zero'})`. Grouped outputs are sorted by stringified keys. Equality follows normal Python dictionary/list semantics; numeric calculations use native numeric arithmetic. No external dependencies beyond the declared package.
