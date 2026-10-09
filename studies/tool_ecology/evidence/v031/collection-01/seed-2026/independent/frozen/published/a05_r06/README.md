# Sales table transforms

Pure-Python, non-mutating service adapters. Public functions all have signature
`adapter(rows, lookup, request)` and return a new list of dictionaries:
`clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' West ', 'date': '2025-03-02', 'units': 2,
         'price_cents': 150}]
clean(rows, [], {'fill': 'zero'})
# [{'region': 'west', 'date': '2025-03-02', 'units': 2, 'price_cents': 150}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 300
group_result = group(rows, [], {'fill': 'zero', 'agg': 'sum'})
```

Missing units are filled by request `fill`: zero, mean, or median (even-sized
median averages its middle values; all missing fills with zero). Clean and the
grouping/lookup families strip/lowercase region strings. Revenue is the product
of filled units and price, or `None` if either operand is missing. Group drops
missing regions; monthly drops missing month/region and uses the first seven
date characters. Both aggregate nonmissing revenue using `sum`, `mean`, or
`count`; empty sum/count are zero and empty mean is `None`. Lookup adds
`revenue_cents_per_target`; missing/unknown/zero target or missing revenue
produces `None`. Window computes mean revenue over trailing ROWS including
current, ignoring missing revenues; width comes from request `window`.
Original columns/order are retained for row-oriented outputs. Inputs are
expected to follow the service schema (numeric values, ISO date strings);
unknown fill/aggregation values fall back to zero/sum. Lookup manager is unused.
