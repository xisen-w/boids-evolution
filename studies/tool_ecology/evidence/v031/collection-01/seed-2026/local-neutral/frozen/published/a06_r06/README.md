# Row-table transformations

Native Python API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns
its complete service-family output as fresh dictionaries and does not mutate inputs.
This package delegates to `published.a06_r05`, whose six families passed all 36
visible service checks with no input mutations.

Example:
```python
from candidate import clean
clean([{'region': ' NW ', 'units': None}], [], {'fill': 'zero'})
# [{'region': 'nw', 'units': 0}]
```

`clean` and derived families support fill `zero`, `mean`, or `median` (even median
averages central values; all-missing is zero). Revenue is null when units or price
is null. Group/monthly accept aggregation `sum`, `mean`, or `count`; missing group
keys are dropped. Lookup uses exact normalized region keys; unknown regions and
zero/missing targets give null ratios. Window uses the trailing configured row
count including the current row and averages non-null revenue. Inputs must follow
the documented service schema and request options; this API adds no validation or
behavior beyond the delegated implementation.
