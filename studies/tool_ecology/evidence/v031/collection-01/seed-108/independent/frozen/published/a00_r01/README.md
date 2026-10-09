# Row transforms

Import with `from candidate import clean, revenue, group, monthly, lookup, window` (or import the respective function directly). Each public function has the exact signature `function(rows, lookup, request)`; `rows` and lookup are lists of dictionaries and request is a dictionary. Calls do not mutate inputs.

All families normalize string regions with strip/lower. Missing units are filled using `request['fill']` (`zero`, `mean`, or `median`; default `zero`); all-missing units fill with zero. Mean and even-sized median use all present units in the input. Revenue is units times price_cents, or None if either is missing. Original columns are retained in row families.

* `clean(rows, lookup, request)`: rows with normalized region and filled units.
* `revenue(rows, lookup, request)`: above plus `revenue_cents`.
* `group(rows, lookup, request)`: list of `{region, <agg>_revenue_cents}`.
* `monthly(rows, lookup, request)`: list of `{month, region, <agg>_revenue_cents}`; month is the first seven date characters.
* `lookup(rows, lookup, request)`: rows plus `revenue_cents_per_target`; unknown/None/zero target and missing revenue produce None. Lookup region strings are normalized as well; duplicate keys use the last lookup row.
* `window(rows, lookup, request)`: rows plus `roll_revenue_cents`, mean of nonmissing revenue in the trailing `request['window']` rows including the current row (`2`, `3`, or `4`).

Aggregations use `request['agg']` (`sum`, `mean`, or `count`; default `sum`), excluding missing revenues. Empty sum/count groups yield zero and empty means yield None. Group rows with missing keys are dropped and results are lexically sorted by stringified keys. No input schema validation beyond these supported parameter choices is provided.

Example:
```python
rows = [{'region': ' West ', 'date': '2025-01-02', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': 'west', 'date': '2025-01-02', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
