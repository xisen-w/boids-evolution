# Tabular service adapters

Public functions `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)` return
new records and do not mutate input data. Example:

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' West ', 'date': '2025-01-02', 'units': None, 'price_cents': 10}]
clean(rows, [], {'fill': 'zero'})
revenue(rows, [], {'fill': 'mean'})
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
monthly(rows, [], {'fill': 'zero', 'agg': 'mean'})
lookup(rows, [{'region': 'west', 'target': 2, 'manager': 'A'}], {'fill': 'zero'})
window(rows, [], {'fill': 'zero', 'window': 2})
```

Fill modes are `zero`, `mean`, and `median`; missing units use the chosen
statistic (all-missing becomes zero). Aggregations are `sum`, `mean`, and
`count`; count counts nonmissing revenue. Region strings are stripped and
lowercased. Grouping excludes missing keys; monthly groups by `date[:7]` and
region. Lookup adds revenue per normalized region target, but not target or
manager. Window means use trailing rows including current. Window widths are
2, 3, or 4. Row-wise services preserve input column values/order and append
derived values. Requires the declared `published.a01_r02` dependency.
