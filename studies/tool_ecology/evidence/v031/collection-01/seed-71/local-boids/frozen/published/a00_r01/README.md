# Table services

Import the adapters from `candidate` (or the published package root). Every public adapter has signature `family(rows, lookup, request)` and returns a new list; inputs are not modified.

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'date': '2024-01-02', 'units': 2,
         'price_cents': 150, 'id': 1}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 300
# group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'north', 'sum_revenue_cents': 300}]
```

`clean` normalizes region (strip/lower) and fills units while retaining row keys. `revenue` additionally derives `revenue_cents`; `group` and `monthly` aggregate nonmissing revenues; `lookup` adds revenue per exact normalized region target; `window` adds trailing-row mean. Fill modes are zero/mean/median (all missing becomes zero); aggregation is sum/mean/count. Group results omit missing keys; empty aggregate mean is null. Lookup does not add lookup fields. These are native Python operations and assume numeric operands and string-like dates in the specified input schema.
