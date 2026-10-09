# Row-table service adapters

Import `candidate` and call `clean(rows, lookup_rows, request)`, `revenue(...)`,
`group(...)`, `monthly(...)`, `lookup(...)`, or `window(...)`. Each returns a new
list of dictionaries and does not mutate input. The six APIs implement the
recurring service contracts: normalized regions and configurable missing-unit
fill; derived revenue; regional/monthly aggregation; exact region target lookup;
and trailing-row revenue mean.

Example:
```python
from candidate import clean
rows = [{'region': ' West ', 'units': None, 'price_cents': 100}]
assert clean(rows, [], {'fill': 'zero'})[0]['region'] == 'west'
```

Fill modes: `zero`, `mean`, `median` (even medians average the central pair;
all-missing fills with zero). Aggregations: `sum`, `mean`, `count`; count
includes only nonmissing revenue. Window widths are 2, 3, or 4 rows. Grouping
drops missing keys and sorting follows stringified keys. Lookup does not add
lookup metadata columns. This package delegates behavior to
`published.a00_r01` and requires that package on `PYTHONPATH`.
