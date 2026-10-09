# tabular_services

Dependency-free Python adapters implementing clean, revenue, group, monthly, lookup, and window. Public functions take `(rows, lookup, request)`; inputs are lists of dictionaries and are not mutated. They return newly copied row dictionaries (or grouped result dictionaries).

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows=[{'id':1, 'region':' West ', 'date':'2024-01-05', 'units':None, 'price_cents':20}]
clean(rows, [], {'fill':'zero'})[0]['region']  # 'west'
revenue(rows, [], {'fill':'zero'})[0]['revenue_cents']  # 0
```

`fill` accepts `zero`, `mean`, or `median`; missing units use the selected statistic (empty/all-missing uses zero). Grouping accepts sum/mean/count, ignores rows with missing grouping keys and ignores missing revenues for aggregation. `monthly` uses the first seven characters of date. Lookup matching uses normalized region keys and adds only the per-target field; missing/zero targets and missing revenue yield None. Window computes trailing row-based means, including the current row. Input fields are retained in insertion order and derived fields appended; group outputs are sorted by stringified key. Values are expected to follow the service schema; dates are expected ISO strings.
