# Tabular adapters

Native Python package, no dependencies. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns new dictionaries and does not mutate inputs. Inputs follow the service schema; request requires `fill` (`zero`, `mean`, `median`), with `agg` (`sum`, `mean`, `count`) for grouping and `window` (2, 3, or 4) for rolling results.

`clean` normalizes region via strip/lower and fills missing units (all missing becomes zero). `revenue` fills units and adds `revenue_cents`, null if units or price is null; it retains region as supplied. `group` and `monthly` normalize region, derive revenue, omit null grouping keys, and aggregate only non-null revenue; output is sorted by stringified keys. Monthly month is the first seven date characters. `lookup` normalizes region and adds only `revenue_cents_per_target`; unknown/null/zero targets and null revenue produce null. `window` adds trailing-row mean of non-null revenues, including current row, and does not normalize region. Original columns are retained and derived columns appended/updated.

```python
from candidate import revenue, group
rows = [{'region':' West ', 'units':None, 'price_cents':25}]
req = {'fill':'zero', 'agg':'sum'}
assert revenue(rows, [], req)[0]['revenue_cents'] == 0
assert group(rows, [], req) == [{'region':'west','sum_revenue_cents':0}]
```

Required fields and valid parameter values are as specified above; dates are expected as ISO date strings.
