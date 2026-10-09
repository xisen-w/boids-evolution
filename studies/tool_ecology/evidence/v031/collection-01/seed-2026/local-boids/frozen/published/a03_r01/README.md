# table_services

Native Python implementations of the clean, revenue, group, monthly, lookup, and window table services. Public adapters all accept `(rows, lookup, request)`; rows and lookup are lists of dictionaries and are not mutated. Requests use `fill` (`zero`, `mean`, `median`) for all adapters; aggregating adapters additionally use `agg` (`sum`, `mean`, `count`), and window uses `window` (2, 3, or 4).

```python
from candidate import clean, revenue, group, monthly, lookup_rate, window
rows = [{'region': ' West ', 'date': '2024-01-02', 'units': None,
         'price_cents': 25}]
request = {'fill': 'zero', 'agg': 'sum', 'window': 2}
print(revenue(rows, [], request))  # region='west', units=0, revenue_cents=0
print(group(rows, [], request))    # [{'region': 'west', 'sum_revenue_cents': 0}]
```

Missing region values stay missing; date month is its first seven characters. Aggregation drops missing keys and excludes missing revenues (empty sum/count are zero and empty mean is None). Lookup region strings are normalized the same way as input regions. Lookup adds no target or manager columns. Derived columns are appended, with existing keys retaining their order. Invalid fill/agg/window values raise ValueError. Inputs are expected to follow the service schema; dates are ISO strings.
