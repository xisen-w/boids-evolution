# Table services

Dependency-free Python package. Public functions each take `(rows, lookup, request)` and return a new list without mutating input data: `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`.

`clean` strips/lowercases non-null regions and fills null units. `revenue` fills units then appends `revenue_cents` (null if units or price is null). Fill policy is `request['fill']`: `zero`, `mean`, or `median`; defaults to `zero`, and all-missing units fill with zero. Median of an even number of values is the central-pair average.

`group` and `monthly` normalize, fill and derive revenue, then aggregate non-null revenue. `request['agg']` is `sum`, `mean`, or `count` (default `sum`); empty sum/count are 0 and empty mean is null. Missing grouping keys are omitted. Group output is sorted by stringified region; monthly adds the first seven date characters (null dates omitted) and sorts by month, region.

`lookup` appends `revenue_cents_per_target`, using normalized region keys from lookup rows. Missing/unknown/zero target or null revenue gives null; lookup columns are not copied. `window` appends `roll_revenue_cents`, the mean of non-null revenues in the trailing `request['window']` rows including current; valid widths are 2, 3, 4. Missing values do not extend the row window.

Example: `revenue([{'units': None, 'price_cents': 8}], [], {'fill':'zero'})` returns `[{'units': 0, 'price_cents': 8, 'revenue_cents': 0}]`. Inputs are expected to be lists of dictionaries following the service schema, with valid policy parameters; date extraction assumes ISO date strings.
