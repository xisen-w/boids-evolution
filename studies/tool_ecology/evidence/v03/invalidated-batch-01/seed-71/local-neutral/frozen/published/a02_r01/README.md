# Native table services

Import the top-level callables with `from candidate import clean, revenue, group, monthly, lookup_service, window`. Each takes `(rows, lookup, request)`; `lookup` is ignored except by `lookup_service`. Inputs are not mutated. Rows retain their original fields and order for row-oriented services; derived keys are appended.

- `clean(rows, lookup, {'fill':'median'})`: normalize region with strip/lower and fill missing units (`zero`, `mean`, or `median`; all-missing gives zero).
- `revenue(...)`: same preparation plus `revenue_cents` (None if an operand is missing).
- `group(..., {'fill':'zero','agg':'sum'})`: group by nonmissing normalized region; `agg` is sum/mean/count of nonmissing revenue.
- `monthly(..., {'agg':'mean'})`: group by month and region, omitting missing keys.
- `lookup_service(rows, lookup, request)`: exact normalized-region target lookup; adds revenue divided by target or None for missing/zero target or revenue.
- `window(..., {'window':3})`: adds trailing row-window revenue mean (supported windows 2, 3, 4).

Example: `revenue([{'region':' West ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})` returns a row with region `west` and revenue_cents `100`. Aggregates are sorted lexicographically by stringified keys. `lookup_service` is named thus to avoid shadowing Python's lookup terminology. Inputs are expected to follow the documented service schema; invalid fill/aggregate/window options raise ValueError.
