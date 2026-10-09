# Sales table services

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`.
Each returns fresh output and does not mutate its inputs. These are thin stable
aliases of the verified `published.a01_r03` service implementations.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' West ', 'date': '2025-01-02', 'units': None,
         'price_cents': 10}]
clean(rows, [], {'fill': 'zero'})
revenue(rows, [], {'fill': 'mean'})
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
monthly(rows, [], {'fill': 'zero', 'agg': 'mean'})
lookup(rows, [{'region': 'west', 'target': 2, 'manager': 'A'}], {'fill': 'zero'})
window(rows, [], {'fill': 'zero', 'window': 2})
```

Fill is `zero`, `mean`, or `median`; all-missing units fill with zero and
median averages the central pair for even counts. Region strings are stripped
and lowercased. Aggregation is `sum`, `mean`, or `count` (nonmissing revenue).
Grouping omits missing keys; monthly groups by `date[:7]` and region. Lookup
uses normalized exact region keys and appends per-target revenue only. Window
computes a trailing-row mean including the current row (width 2, 3, or 4).
Row-wise results preserve source columns and order, then append derived fields;
group results are sorted by stringified keys. Empty/missing values follow the
service contract. Requires `published.a01_r03`.
