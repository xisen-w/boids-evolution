# Tabular service adapters

This package re-exports tested native implementations from the explicitly bundled `a04_r02` dependency. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns fresh dictionaries/lists and does not mutate the inputs.

`clean` normalizes region strings with strip/lower and fills missing units. `revenue` fills units and derives `revenue_cents` (None when an operand is missing). Group and monthly aggregate nonmissing revenue (`sum`, `mean`, or `count`), dropping missing keys and sorting stringified keys. Lookup adds per-target revenue using exact region keys; unknown regions, absent/zero targets, or missing revenue produce None. Window adds a trailing ROWS mean over nonmissing revenue, including the current row. Fill is `zero`, `mean`, or `median`; all-missing values fill with zero, and even medians average the central pair. Window accepts 2, 3, or 4.

Example:
```python
from candidate import revenue
revenue([{'units': None, 'price_cents': 5}], [], {'fill': 'zero'})
# [{'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```
Limitations: inputs follow the service contract (row dictionaries, valid request choices, numeric values); this API does not validate arbitrary malformed schemas.
