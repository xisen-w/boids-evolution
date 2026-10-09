# Row table services

Import `clean, revenue, group, monthly, lookup, window` from `candidate`. Each accepts `(rows, lookup, request)` and returns new row dictionaries; inputs are not mutated. `clean` fills missing units and normalizes region; `revenue` fills units and appends `revenue_cents`; `group` and `monthly` aggregate nonmissing revenues; `lookup` appends revenue per normalized region target; `window` appends the trailing row-window mean.

Fill is selected with `request['fill']` (`zero`, `mean`, `median`; default zero; all missing becomes zero). Aggregation uses `request['agg']` (`sum`, `mean`, `count`; default sum). Window uses `request['window']` (2, 3, or 4). Example: `revenue([{'units':2,'price_cents':50}], [], {'fill':'zero'})` gives `[{'units':2,'price_cents':50,'revenue_cents':100}]`.

All existing columns and order are preserved with derived columns appended. Revenue/window do not normalize region. Grouped services normalize region and sort keys. Inputs are expected to contain mapping rows and numeric values; dates, when present, are ISO strings. Invalid fill, aggregation, or window values raise `ValueError`.
