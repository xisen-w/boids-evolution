# Table services
Pure Python table transformations. All functions take `(rows, lookup, request)`, copy inputs, and return fresh results.

- `clean`: normalize region using strip/lower and impute missing units.
- `revenue`: impute units then append `revenue_cents`; does not normalize region.
- `group`: normalize region, calculate revenue and group nonmissing regions using request `agg` (`sum`, `mean`, `count`).
- `monthly`: same revenue processing grouped by month (`date[:7]`) and region.
- `lookup`: normalized region exact-match lookup; adds only `revenue_cents_per_target` (manager omitted).
- `window`: append trailing-row mean `roll_revenue_cents` using request `window`.

`request.fill` accepts `zero`, `mean`, `median` (all missing fills zero); `request.agg` accepts sum/mean/count. Example: `revenue([{'units':2,'price_cents':50}], [], {'fill':'zero'})[0]['revenue_cents'] == 100`. Revenue is None if either operand is None. Missing group keys are dropped; empty aggregate semantics follow sum/count=0 and mean=None. Dates should be ISO strings; malformed/missing dates are not validated.
