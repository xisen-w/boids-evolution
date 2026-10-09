# Row-table services

Native Python implementations of six services. Public functions `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)` return fresh output dictionaries and do not mutate inputs.

Example:
```python
from candidate import monthly
monthly([{'region':' West ', 'date':'2025-03-12', 'units':2, 'price_cents':50}], [], {'fill':'mean', 'agg':'sum'})
# [{'month': '2025-03', 'region': 'west', 'sum_revenue_cents': 100}]
```

Fill is `zero`, `mean`, or `median`; a missing-only units column fills with zero, and even medians average the middle values. Row-oriented revenue is units times price (None if price is missing); group and monthly normalize regions and aggregate only nonmissing revenues, dropping missing keys. Lookup normalizes exact region keys and returns None for unknown/zero/missing targets or missing revenue. Window computes a mean over the trailing `request['window']` rows (2, 3, or 4), excluding missing revenue values but retaining row positions. Group aggregations are `sum`, `mean`, or `count`; count counts nonmissing revenues. Empty sum/count groups are zero and empty means None. Row-oriented outputs preserve input columns and order; aggregate outputs contain only keys and aggregate. Inputs are expected to follow the supplied schema and valid option values.
