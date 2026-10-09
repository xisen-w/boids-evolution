# Native table services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`. Every public callable has signature `(rows, lookup, request)`; `rows` and lookup are lists of dictionaries, and inputs are not mutated. Results are new dictionaries/lists. `request.fill` is `zero`, `mean`, or `median` (missing units are filled across the input, all-missing becomes zero); aggregate requests use `request.agg` = `sum`, `mean`, or `count`; window requests use `request.window` = 2, 3, or 4.

Regions are stripped and lowercased. `clean` returns original columns with normalized region and filled units. `revenue` additionally appends `revenue_cents`, null when price or units is null. Group and monthly return only their grouping keys and `<agg>_revenue_cents`, omit null group keys, and sort by keys. Group count excludes missing revenue. Monthly uses the first seven date characters. Lookup appends `revenue_cents_per_target`; target regions are normalized like row regions, and missing/zero targets yield null. Window appends a trailing-row (including current row) mean, ignoring null revenues and returning null for an all-null window.

Example: `revenue([{'region':' West ','units':2,'price_cents':50}], [], {'fill':'zero'})` returns a row with normalized region `west` and revenue 100.

These APIs expect the documented dictionary-shaped inputs and valid request options; malformed dates and nonnumeric values are not specially handled.
