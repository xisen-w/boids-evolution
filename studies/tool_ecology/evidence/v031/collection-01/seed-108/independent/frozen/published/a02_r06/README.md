# Row-table service adapters

Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`.
All return new lists of dictionaries and do not mutate inputs. The implementation
reuses the verified `published.a02_r05` package (dependency declared in publish.json).

Services normalize regions, fill units (`fill`: `zero`, `mean`, `median`), calculate
revenue, aggregate region/month groups (`agg`: `sum`, `mean`, `count`), perform
region target lookup, or calculate trailing ROWS revenue means (`window`: 2/3/4),
respectively. Missing values and output column ordering follow the service contract;
unknown lookup regions and invalid operands produce `None` where specified. Invalid
options are rejected by the underlying implementation.

Example:
```python
from candidate import revenue
r = revenue([{'region': ' West ', 'units': 2, 'price_cents': 30}], [], {'fill': 'zero'})
assert r[0]['region'] == 'west' and r[0]['revenue_cents'] == 60
```
