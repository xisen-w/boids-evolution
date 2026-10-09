# Row transforms

Dependency-free native Python functions. Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts a list of dictionaries, lookup table (empty for all except lookup), and request dictionary, returning new data without mutating inputs.

`clean` normalizes region via strip/lower and fills missing units; `fill` is `zero`, `mean`, or `median` (default zero), and an all-missing column fills with zero. `revenue` fills units and appends `revenue_cents`, null when units or price is null, preserving other fields and their order. `group` normalizes region and groups non-null region keys; `monthly` additionally groups by the first seven date characters and drops null month/region. Both accept `agg`=`sum`, `mean`, or `count` (default sum), count only non-null revenue, emit only aggregate fields, and sort by stringified keys; empty sum/count are zero and empty mean is null. `lookup` normalizes region, appends `revenue_cents_per_target` from exact region matches; absent/zero target or null revenue gives null. `window` appends `roll_revenue_cents`, the mean of non-null revenue in the trailing `window` rows including current (`2`, `3`, or `4`; default 2), or null if no values. Row transforms preserve original field order and append derived fields.

Example:
```python
revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
Limitations: inputs are expected to follow the specified table schemas and request modes; invalid modes raise `ValueError`. Lookup uses exact region keys (the rows' regions are normalized, lookup keys are not).
