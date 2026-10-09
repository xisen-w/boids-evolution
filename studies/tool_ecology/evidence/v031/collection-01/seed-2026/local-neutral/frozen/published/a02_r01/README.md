# Table service transformations

Import the top-level functions with `from candidate import clean, revenue, group, monthly, lookup, window`. Each accepts `(rows, lookup, request)`; rows and lookup are lists of dictionaries, and inputs are not mutated. `clean` normalizes string regions by strip/lower and fills absent/None units according to request `fill` (`zero`, `mean`, or `median`; default `zero`; all-missing gives zero). `revenue` does the same and appends `revenue_cents`, null if units or price is null. Existing dictionary keys retain their order; derived keys are appended.

`group` aggregates non-null revenue by non-null normalized region; `monthly` groups by non-null region and first seven date characters. Both use request `agg` (`sum`, `mean`, `count`; default `sum`), omit missing group keys, and sort keys lexicographically. Empty sum/count yield zero and empty mean yields null. Count counts non-null revenue.

`lookup` adds `revenue_cents_per_target` using exact lookup region keys; absent/null/zero target and null revenue yield null. It does not add lookup columns. `window` adds `roll_revenue_cents`, the mean of non-null revenue in the trailing physical rows including current; request `window` defaults to 2.

Example: `revenue([{'region':' EAST ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})` returns `[{'region':'east','units':2,'price_cents':50,'revenue_cents':100}]`. Missing expected columns are treated as null where applicable. Inputs are expected to have valid request choices and numeric values; date grouping uses `date[:7]` without validating ISO syntax.
