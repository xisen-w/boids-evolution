# Row-table services

Import the package as `candidate` (with its declared `published.a04_r02` dependency available). Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts a list of row dictionaries, lookup records, and a request dictionary and returns a new list; inputs are not modified.

* `clean`: strip/lower region; fill missing units using `request['fill']` (`zero`, `mean`, `median`; absent values default to zero). All-missing units become zero. Keeps every column and row order.
* `revenue`: fill units and append `revenue_cents` (units times price, or `None` if either is missing). Region remains verbatim; original columns/order are preserved.
* `group`: normalized region and derived revenue, then group by nonmissing region. `request['agg']` chooses `sum`, `mean`, or nonmissing-revenue `count`; output is region plus `<agg>_revenue_cents`, sorted by stringified region.
* `monthly`: as above, groups by nonmissing `date[:7]` month and normalized region; output month, region and aggregate, sorted by stringified keys.
* `lookup`: normalized region and revenue, with `revenue_cents_per_target` from exact normalized region lookup. Unknown/missing/zero target or missing revenue gives `None`; target and manager are not added.
* `window`: revenue plus `roll_revenue_cents`, mean of nonmissing revenues within trailing `request['window']` rows including current (default 2); `None` for a window with no revenue.

Example:
```python
from candidate import clean, revenue
clean([{'region': ' North ', 'units': None}], [], {'fill': 'zero'})
# [{'region': 'north', 'units': 0}]
revenue([{'region': ' North ', 'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```

Rows are expected to follow the service schema; monthly expects a date string suitable for its first-seven-character month. Unsupported fill values fall back to zero; unsupported aggregates use sum. Arithmetic assumes numeric inputs and does not mutate inputs.
