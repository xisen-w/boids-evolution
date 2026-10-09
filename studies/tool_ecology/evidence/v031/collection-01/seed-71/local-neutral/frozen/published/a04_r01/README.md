# Tabular services

Import with `from candidate import clean, revenue, group, monthly, lookup, window`. Each public function takes `(rows, lookup, request)`; `rows` and `lookup` are lists of dictionaries, `request` supplies `fill` and (for group/monthly) `agg`, or (for window) `window`. Inputs are not mutated.

`clean` normalizes non-null region strings by strip/lower and fills missing units. `revenue` fills units then appends `revenue_cents`. `group` and `monthly` normalize regions and aggregate nonmissing revenue, dropping null grouping keys; monthly takes the first seven date characters. Aggregates are `sum`, `mean`, and `count`; empty sum/count are zero and empty mean is null. `lookup` appends `revenue_cents_per_target` using normalized region keys. `window` appends the mean of nonmissing revenues in the trailing `window` rows, including the current row.

Example:
```python
rows = [{'region': ' West ', 'units': None, 'price_cents': 20, 'date': '2025-01-03'}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' West ', 'units': 0, 'price_cents': 20, 'date': '2025-01-03', 'revenue_cents': 0}]
clean(rows, [], {'fill': 'mean'}) # region is 'west'
```

Fill policies are `zero`, `mean`, and `median` (even medians average central values; all-missing fills with zero). Lookup keys are normalized identically; later duplicate keys take precedence. Missing values are represented by `None`. Window sizes are 2, 3, or 4. These functions preserve input row order and original fields; derived fields are appended or replaced in place if already present. Invalid policy names raise `ValueError`.
