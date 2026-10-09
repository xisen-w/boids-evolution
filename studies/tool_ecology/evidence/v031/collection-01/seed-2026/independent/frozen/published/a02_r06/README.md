# Tabular service adapters

Native Python root functions wrap the verified `published.a02_r02` implementations. All functions accept `(rows, lookup, request)` and return new row dictionaries (or grouped result dictionaries); inputs are not mutated.

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'north', 'sum_revenue_cents': 100}]
```

`clean` normalizes region and fills missing units. `revenue` fills units and adds revenue. `group` and `monthly` normalize region, derive revenue, and aggregate; `lookup` additionally derives revenue per region target; `window` adds trailing-row mean revenue. Fill modes are `zero`, `mean`, and `median` (even median averages central values; all-missing fills zero). Aggregations are `sum`, `mean`, `count` (count ignores missing revenue). Window widths are 2, 3, or 4 and include the current row. Missing grouping keys are dropped; mean of no values is `None`, empty sum/count is zero. Lookup unknown/zero/missing targets yield `None`. Dates are grouped by their first seven characters. Request values are expected to use the supported options; inputs follow the documented tabular schema.
