# Row table transforms

Dependency-free Python transforms returning fresh row dictionaries; inputs are not mutated.

Public APIs: `clean(rows, request)`, and `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, `window(rows, lookup, request)`. Each of the latter APIs accepts the unused lookup argument for a consistent service signature.

`clean` normalizes string region values using strip/lower and fills missing units. Revenue-related services fill missing units and append `revenue_cents` (None if units or price is None); they preserve region as supplied. Fill methods are `zero`, `mean`, `median` (even-sized median is the central-value average), defaulting to zero; all-missing units become zero. Group and monthly aggregate nonmissing revenue using sum/mean/count (`request['agg']`, default sum), dropping missing group keys. Empty mean aggregates are None. Monthly uses `date[:7]`. Lookup normalizes region keys and appends revenue per target, None for unknown/zero/None targets or missing revenue. Window appends the mean of available revenues in the trailing `request['window']` rows (2, 3, or 4), including current row.

Example:

```python
from candidate import revenue, clean
rows = [{'region':' East ', 'units':None, 'price_cents':50}]
assert clean(rows, {'fill':'zero'})[0]['region'] == 'east'
assert revenue(rows, [], {'fill':'zero'})[0]['revenue_cents'] == 0
```

Inputs are sequences of mappings with numeric units/prices and ISO-like date strings; invalid fill, aggregation, and window options raise ValueError. No target or manager columns are added.
