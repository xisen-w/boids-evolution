# Table service transformations

Native Python, no dependencies. Public service adapters all accept `(rows, lookup, request)`; inputs are not mutated. Rows are dictionaries and output row dictionaries are copies.

* `clean(rows, lookup, request)`: normalizes string regions with strip/lower and fills missing units.
* `revenue(...)`: same, appending `revenue_cents` (None when price or units is missing).
* `group(...)`: groups by normalized nonmissing region and returns `region` plus `<agg>_revenue_cents`.
* `monthly(...)`: groups by nonmissing `date[:7]` and region; output has `month`, `region`, and aggregate field.
* `lookup(...)`: appends `revenue_cents_per_target`; missing/zero targets and missing revenue produce None. Lookup keys are normalized region strings; manager/target are not added to rows.
* `window(...)`: appends `roll_revenue_cents`, the mean of nonmissing revenue in trailing `window` rows.

Example: `revenue([{'region':' NORTH ', 'units':2, 'price_cents':30}], [], {'fill':'zero'})` returns a row with region `north` and revenue 60. Fill is `zero`, `mean`, or `median` (all-missing becomes zero); aggregation is `sum`, `mean`, or `count`. Empty aggregate groups naturally produce no output. Group count counts only nonmissing revenues. Group results are sorted by stringified keys. Other original columns and their order are preserved before appended derived columns. Unsupported request options raise ValueError; expected input schema is the service schema, and date values are ISO strings or None.
