# Row transforms

Import the six top-level callables: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each takes a list of row dictionaries, lookup rows (unused except by the lookup transform), and a request dictionary. They return new dictionaries/lists and do not mutate inputs.

`clean` normalizes string regions with strip/lower and fills missing units using request `fill` (`zero`, `mean`, or `median`; all missing becomes zero), preserving columns and order. `revenue` adds `revenue_cents`, null when units or price are null. `group` and `monthly` additionally need request `agg` (`sum`, `mean`, `count`); they drop missing group keys and return the specified grouped schema. `lookup` adds `revenue_cents_per_target`, matching normalized region keys and yielding null for absent/zero targets or revenue. `window` needs `window` equal to 2, 3, or 4, and adds the trailing row-window mean of nonnull revenue.

Example: `revenue([{'region':' West ','units':2,'price_cents':50}], [], {'fill':'zero'})` returns a row with region `west` and revenue 100. Required row keys are those relevant to each operation; invalid fill/aggregation/window values raise `ValueError`.
